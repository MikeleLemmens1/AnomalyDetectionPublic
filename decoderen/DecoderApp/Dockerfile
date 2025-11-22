FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env

COPY ./DecoderApp ./DecoderApp
RUN rm -rf ./DecoderApp/out/

# Restore dependencies
RUN dotnet restore DecoderApp/DecoderApp.vbproj

# Build and publish a release
RUN dotnet publish DecoderApp/DecoderApp.vbproj -c Release -r linux-x64 -o DecoderApp/out

# Build runtime image
# FROM mcr.microsoft.com/dotnet/runtime:8.0
# WORKDIR /DecoderApp
# COPY --from=build-env bin .
# ENTRYPOINT ["dotnet", "DataDecoder.dll"]