#!/usr/bin/env bash

function generate() {
  alembic revision --m="${NAME}" --autogenerate
}

function migrate() {
  alembic upgrade head
}

function rollback() {
  alembic downgrade -1
}