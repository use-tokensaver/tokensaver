# syntax=docker/dockerfile:1

# Builds on the host's architecture and cross-compiles — pure Go, no cgo — so
# the arm64 image needs no emulation.
FROM --platform=$BUILDPLATFORM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY cmd ./cmd
COPY internal ./internal
ARG TARGETOS TARGETARCH VERSION=dev
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -trimpath -ldflags "-s -w -X main.version=${VERSION}" -o /out/tokensaver ./cmd/tokensaver

# distroless/static has CA certificates (HTTPS fetches) and nothing else.
FROM gcr.io/distroless/static-debian12:nonroot
LABEL org.opencontainers.image.source="https://github.com/use-tokensaver/tokensaver" \
      org.opencontainers.image.description="Local MCP server that turns web pages, PDFs, Office files and JSON into compact, LLM-ready text" \
      org.opencontainers.image.licenses="MIT" \
      io.modelcontextprotocol.server.name="io.github.use-tokensaver/tokensaver"
COPY --from=build /out/tokensaver /usr/local/bin/tokensaver
ENTRYPOINT ["/usr/local/bin/tokensaver"]
