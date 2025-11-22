FROM mcr.microsoft.com/mssql/server:2022-latest

# Add the sqlcmd path to the PATH environment variable
ENV PATH="/opt/mssql-tools18/bin:${PATH}"

USER root

# Install necessary packages and sqlpackage
# wget : for fetchin other sqlpackage
# unzip : for unzipping sqlpackage
# sqlpackage : for loading .bacpac file
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://aka.ms/sqlpackage-linux -O /opt/sqlpackage.zip && \
    unzip /opt/sqlpackage.zip -d /opt/sqlpackage && \
    chmod +x /opt/sqlpackage/sqlpackage && \
    rm /opt/sqlpackage.zip

USER mssql