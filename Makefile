STOCK_DB_ALEMBIC = alembic -c src/apps/stock_data_management/alembic.ini

.PHONY: stock-db-revision
stock-db-revision:
	$(STOCK_DB_ALEMBIC) revision --autogenerate -m "$(msg)"

.PHONY: stock-db-upgrade
stock-db-upgrade:
	$(STOCK_DB_ALEMBIC) upgrade head

.PHONY: stock-db-downgrade
stock-db-downgrade:
	$(STOCK_DB_ALEMBIC) downgrade -1

.PHONY: stock-db-current
stock-db-current:
	$(STOCK_DB_ALEMBIC) current

.PHONY: stock-db-history
stock-db-history:
	$(STOCK_DB_ALEMBIC) history