CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra

SRCDIR   := src
BUILDDIR := build

HEADERS  := $(wildcard $(SRCDIR)/*.h)
SRCS     := $(wildcard $(SRCDIR)/*.cpp)
OBJS     := $(patsubst $(SRCDIR)/%.cpp,$(BUILDDIR)/%.o,$(SRCS))

ifeq ($(OS),Windows_NT)
    TARGET := SocialMedia.exe
    MKDIR   = powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path $(BUILDDIR) | Out-Null"
    RMCMD   = powershell -NoProfile -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $(BUILDDIR),$(TARGET); exit 0"
else
    TARGET := SocialMedia
    MKDIR   = mkdir -p $(BUILDDIR)
    RMCMD   = rm -rf $(BUILDDIR) $(TARGET)
endif

ifeq ($(DEBUG), 1)
    CXXFLAGS := $(CXXFLAGS_COMMON) -g3 -O0
    BUILD_MSG := "--- BUILDING IN DEBUG MODE (-g3 -O0) ---"
else
    CXXFLAGS := $(CXXFLAGS_COMMON) -O2
    BUILD_MSG := "--- BUILDING IN RELEASE MODE (-O2) ---"
endif

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

$(BUILDDIR)/%.o: $(SRCDIR)/%.cpp $(HEADERS)
	$(MKDIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	$(RMCMD)

rebuild: clean all

.PHONY: all clean rebuild
