include .env

reset:
	docker compose --profile setup down
	docker volume rm dep2-mssql-server-data
	docker compose --profile setup up -d --build

# When an error shows while making a docker reset or fresh compose up.
# Run make netwerk-down
# Docker container mssqldb likely succeeded and mssqldb.configurator started,
# however it failed somehow. This is a fix
netwerk-down:
	docker compose --profile setup down
	docker compose --profile setup up -d --build


db-crh-present-check:
	sqlcmd -S localhost -U sa -P ${MSSQL_SA_PASSWORD} -C -Q "SELECT name FROM sys.databases;"
	sqlcmd -S localhost -U sa -P ${MSSQL_SA_PASSWORD} -C -d "CRH" -Q "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;"
	sqlcmd -S localhost -U sa -P ${MSSQL_SA_PASSWORD} -C -d "CRH" -Q "SELECT InstanceID, COUNT(InstanceID) as amount FROM Candidate GROUP BY InstanceID ORDER BY COUNT(InstanceID) DESC;"
	
