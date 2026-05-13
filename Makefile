CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2
SRCS     := FriendsSuggestion.cpp SocialMedia.cpp
OBJS     := $(SRCS:.cpp=.o)

# Detect OS: set executable extension and delete command
ifeq ($(OS),Windows_NT)
    TARGET := FriendsSuggestion.exe
    RMCMD  = powershell -NoProfile -Command "Remove-Item -Force -ErrorAction SilentlyContinue *.o,*.exe"
else
    TARGET := FriendsSuggestion
    RMCMD  = rm -f $(OBJS) $(TARGET)
endif

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp SocialMedia.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	$(RMCMD)

rebuild: clean all

.PHONY: all clean rebuild
