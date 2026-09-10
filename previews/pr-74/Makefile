.PHONY: help install serve stop build clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install Ruby dependencies via bundler"
	@echo "  make serve      - Start Jekyll server for local viewing (with live reload)"
	@echo "  make stop       - Stop the running Jekyll server"
	@echo "  make build      - Build site for local edits"
	@echo "  make clean      - Remove generated files (_site, .sass-cache)"

install:
	@echo "Installing Ruby dependencies..."
	@if ! command -v bundle >/dev/null 2>&1; then \
		echo "Error: bundler is not installed. Install it with: gem install bundler"; \
		exit 1; \
	fi
	@bundle install || { \
		echo ""; \
		echo "Bundle install failed. Common solutions:"; \
		echo "  1. Install Xcode Command Line Tools: xcode-select --install"; \
		echo "  2. Update Ruby version (current: $(shell ruby -v))"; \
		echo "  3. Check the error message above for specific gem failures"; \
		exit 1; \
	}

serve:
	bundle exec jekyll serve

stop:
	@echo "Stopping Jekyll server..."
	@pkill -f "jekyll serve" || echo "No Jekyll server found running"

build:
	bundle exec jekyll build

clean:
	rm -rf _site .sass-cache