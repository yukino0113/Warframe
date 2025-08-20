import datetime
import decimal
from typing import Optional

from sqlalchemy import Column, DECIMAL, Integer, TIMESTAMP, Table, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AdditionalItemDropsBySource(Base):
    __tablename__ = "additional_item_drops_by_source"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class BlueprintDropsByItem(Base):
    __tablename__ = "blueprint_drops_by_item"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class BlueprintDropsBySource(Base):
    __tablename__ = "blueprint_drops_by_source"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class BountyRewards(Base):
    __tablename__ = "bounty_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rotation: Mapped[str] = mapped_column(Text, nullable=False)
    stage: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class DynamicLocationRewards(Base):
    __tablename__ = "dynamic_location_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rotation: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class KeyRewards(Base):
    __tablename__ = "key_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rotation: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


t_last_update = Table(
    "last_update", Base.metadata, Column("time", Integer, nullable=False)
)


class MissionRewards(Base):
    __tablename__ = "mission_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rotation: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class ModDropsByMod(Base):
    __tablename__ = "mod_drops_by_mod"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class ModDropsBySource(Base):
    __tablename__ = "mod_drops_by_source"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class PrimeParts(Base):
    __tablename__ = "prime_parts"

    warframe_set: Mapped[str] = mapped_column(Text, nullable=False)
    parts_name: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)


class RelicDropsBySource(Base):
    __tablename__ = "relic_drops_by_source"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class RelicRewards(Base):
    __tablename__ = "relic_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    radiant: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    relic: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class ResourceDropsByResource(Base):
    __tablename__ = "resource_drops_by_resource"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class ResourceDropsBySource(Base):
    __tablename__ = "resource_drops_by_source"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class SigilDropsBySource(Base):
    __tablename__ = "sigil_drops_by_source"

    item: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class SortieRewards(Base):
    __tablename__ = "sortie_rewards"

    prize: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[str] = mapped_column(Text, nullable=False)
    drop_rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )


class VaultStatus(Base):
    __tablename__ = "vault_status"

    warframe_set: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    set_type: Mapped[str] = mapped_column(Text, nullable=False)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)


# ----- Group class -----


class RewardTables:
    TABLES = [
        BountyRewards,
        DynamicLocationRewards,
        KeyRewards,
        MissionRewards,
        SortieRewards,
    ]
