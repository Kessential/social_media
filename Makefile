CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2

SRCDIR   := src
BUILDDIR := build

SRCS     := $(wildcard $(SRCDIR)/*.cpp)
OBJS     := $(patsubst $(SRCDIR)/%.cpp,$(BUILDDIR)/%.o,$(SRCS))

ifeq ($(OS),Windows_NT)
    TARGET := SocialMedia.exe
    MKDIR   = powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path $(BUILDDIR) | Out-Null"
    RMCMD   = powershell -NoProfile -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $(BUILDDIR),$(TARGET)"
else
    TARGET := SocialMedia
    MKDIR   = mkdir -p $(BUILDDIR)
    RMCMD   = rm -rf $(BUILDDIR) $(TARGET)
endif

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

$(BUILDDIR)/%.o: $(SRCDIR)/%.cpp $(SRCDIR)/SocialMedia.h
	$(MKDIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	$(RMCMD)

rebuild: clean all

.PHONY: all clean rebuild
