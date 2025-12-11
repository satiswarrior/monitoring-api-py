from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    TIMESTAMP,
    Boolean,
    Index,
    ForeignKey,
    func,
    text,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.database import Base


# Postgres ENUM definitions (names must match those used in raw SQL schema)
AlertSeverityEnum = SAEnum(
    "Normal",
    "Minor",
    "Major",
    "Critical",
    name="alert_severity",
)
CommandTypeEnum = SAEnum(
    "DELETE_ALERT",
    "CUSTOM",
    name="command_type",
)
CommandStatusEnum = SAEnum(
    "pending",
    "sent",
    "done",
    "failed",
    name="command_status",
)
ResultStatusEnum = SAEnum(
    "success",
    "failed",
    name="result_status",
)
UserRoleEnum = SAEnum(
    "admin",
    "viewer",
    name="user_role",
)


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    servers = relationship("Server", back_populates="region", cascade="all, delete-orphan")


class Server(Base):
    __tablename__ = "servers"

    # id is accepted from agents, so no autoincrement
    id = Column(BigInteger, primary_key=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="SET NULL"), nullable=True)
    ip = Column(Text)
    cgm_version = Column(Text)
    admin_version = Column(Text)
    last_update = Column(TIMESTAMP(timezone=True))
    last_status = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    region = relationship("Region", back_populates="servers")
    agent_keys = relationship("AgentKey", back_populates="server", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="server", cascade="all, delete-orphan")
    commands = relationship("CommandQueue", back_populates="server", cascade="all, delete-orphan")


Index("idx_servers_region", Server.region_id)
Index("idx_servers_last_update", Server.last_update)


class AgentKey(Base):
    __tablename__ = "agent_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    server_id = Column(BigInteger, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)

    server = relationship("Server", back_populates="agent_keys")


Index("idx_agent_keys_server", AgentKey.server_id)
# Unique index for key_hash
Index("uq_agent_keys_keyhash", AgentKey.key_hash, unique=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    server_id = Column(BigInteger, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    severity = Column(AlertSeverityEnum, nullable=False)
    source = Column(Text)
    alert_text = Column(Text, nullable=False)
    counter = Column(Integer, server_default=text("1"), nullable=False)
    stacktrace = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    active = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    server = relationship("Server", back_populates="alerts")


Index("idx_alerts_server_active", Alert.server_id, Alert.active)
Index("idx_alerts_severity", Alert.severity)


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    server_id = Column(BigInteger)
    severity = Column(AlertSeverityEnum)
    source = Column(Text)
    alert_text = Column(Text)
    counter = Column(Integer)
    stacktrace = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True))
    archived_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


Index("idx_alert_history_server", AlertHistory.server_id)


class CommandQueue(Base):
    __tablename__ = "command_queue"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    server_id = Column(BigInteger, ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    type = Column(CommandTypeEnum, nullable=False)
    payload = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    executed_at = Column(TIMESTAMP(timezone=True))
    status = Column(CommandStatusEnum, server_default=text("'pending'"), nullable=False)
    correlation_id = Column(UUID(as_uuid=True))
    attempts = Column(Integer, server_default=text("0"), nullable=False)
    ttl_until = Column(TIMESTAMP(timezone=True))

    server = relationship("Server", back_populates="commands")
    results = relationship("CommandResult", back_populates="command", cascade="all, delete-orphan")


Index("idx_commands_server_status", CommandQueue.server_id, CommandQueue.status)
Index("idx_commands_status_created", CommandQueue.status, CommandQueue.created_at)


class CommandResult(Base):
    __tablename__ = "command_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    command_id = Column(BigInteger, ForeignKey("command_queue.id", ondelete="CASCADE"), nullable=False)
    status = Column(ResultStatusEnum, nullable=False)
    message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    command = relationship("CommandQueue", back_populates="results")


Index("idx_command_results_command", CommandResult.command_id)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(UserRoleEnum, server_default=text("'viewer'"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True))

    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


Index("idx_admin_role", AdminUser.role)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("admin_users.id"))
    actor_type = Column(Text)
    action = Column(Text, nullable=False)
    payload = Column(JSONB)
    remote_addr = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("AdminUser", back_populates="audit_logs")


Index("idx_audit_created", AuditLog.created_at)
