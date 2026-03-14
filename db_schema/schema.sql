-- Aktual'naya skhema bazy dannykh proekta university rooms
-- SUBD: PostgreSQL 16
-- Sgenerirovano iz Django migratsiy (rooms/0001_initial + rooms/0002_add_capacity_to_room)
-- Data: 2026-03-14

BEGIN;

--
-- Create model Building
--
CREATE TABLE "rooms_building" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "address" varchar(500) NOT NULL DEFAULT '',
    "description" text NOT NULL DEFAULT ''
);

--
-- Create model RoomPurpose
--
CREATE TABLE "rooms_roompurpose" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL
);

--
-- Create model RoomType
--
CREATE TABLE "rooms_roomtype" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL
);

--
-- Create model Department
--
CREATE TABLE "rooms_department" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "department_type" varchar(20) NOT NULL,
    "parent_id" bigint NULL REFERENCES "rooms_department" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "rooms_department_parent_id_72b4b691" ON "rooms_department" ("parent_id");

--
-- Create model Location
--
CREATE TABLE "rooms_location" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "ceiling_height" numeric(5, 2) NOT NULL,
    "building_id" bigint NOT NULL REFERENCES "rooms_building" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "rooms_location_building_id_34ca5d63" ON "rooms_location" ("building_id");

--
-- Create model Room (with capacity field from migration 0002)
--
CREATE TABLE "rooms_room" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "room_number" varchar(50) NOT NULL,
    "width" numeric(8, 2) NOT NULL,
    "length" numeric(8, 2) NOT NULL,
    "capacity" integer NOT NULL DEFAULT 0 CHECK ("capacity" >= 0),
    "building_id" bigint NOT NULL REFERENCES "rooms_building" ("id") DEFERRABLE INITIALLY DEFERRED,
    "department_id" bigint NULL REFERENCES "rooms_department" ("id") DEFERRABLE INITIALLY DEFERRED,
    "location_id" bigint NOT NULL REFERENCES "rooms_location" ("id") DEFERRABLE INITIALLY DEFERRED,
    "purpose_id" bigint NULL REFERENCES "rooms_roompurpose" ("id") DEFERRABLE INITIALLY DEFERRED,
    "room_type_id" bigint NULL REFERENCES "rooms_roomtype" ("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX "rooms_room_building_id_3f238d19" ON "rooms_room" ("building_id");
CREATE INDEX "rooms_room_department_id_768027e9" ON "rooms_room" ("department_id");
CREATE INDEX "rooms_room_location_id_6c033dfb" ON "rooms_room" ("location_id");
CREATE INDEX "rooms_room_purpose_id_faa6f4f4" ON "rooms_room" ("purpose_id");
CREATE INDEX "rooms_room_room_type_id_d6bd9615" ON "rooms_room" ("room_type_id");

COMMIT;
