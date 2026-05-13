CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2
TARGET   := FriendsSuggestion.exe
SRCS     := FriendsSuggestion.cpp SocialMedia.cpp
OBJS     := $(SRCS:.cpp=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ 

%.o: %.cpp SocialMedia.h
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f *.o *.exe nul

rebuild: clean all

.PHONY: all clean rebuild
