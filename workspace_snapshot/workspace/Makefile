traffic:
	python scripts/export_traffic.py $(MONTH)

rollup:
	python scripts/weekly_rollup.py

inventory:
	python scripts/inventory_check.py inventory/snapshot_$(DATE).csv
