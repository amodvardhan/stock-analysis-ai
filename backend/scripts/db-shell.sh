#!/bin/bash
# Open PostgreSQL shell

docker-compose exec postgres psql -U aihub_user -d aihub_stock_intelligence
