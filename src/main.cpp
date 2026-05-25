#include "SocialMedia.h"
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#ifdef _WIN32
#include <windows.h>
#endif

// Xóa buffer input
void clearInput() {
  std::cin.clear();
  std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

// Đọc số nguyên an toàn
int readInt(const std::string &prompt) {
  int val;
  while (true) {
    std::cout << prompt;
    if (std::cin >> val) {
      return val;
    }
    if (std::cin.eof()) {
      std::cerr << "\n[LOI] Het du lieu dau vao!\n";
      exit(0);
    }
    std::cout << "[LOI] Vui long nhap so nguyen!\n";
    clearInput();
  }
}

// Đọc chuỗi (có khoảng trắng)
std::string readLine(const std::string &prompt) {
  std::string line;
  std::cout << prompt;
  std::getline(std::cin, line);
  return line;
}

void printMenu() {
  std::cout << "\n";
  std::cout << "╔═════════════════════════════════════════════════╗\n";
  std::cout << "║          MANG XA HOI - MO PHONG BFS             ║\n";
  std::cout << "╠═════════════════════════════════════════════════╣\n";
  std::cout << "║  1.  Tai du lieu tu file                        ║\n";
  std::cout << "║  2.  Them nguoi dung                            ║\n";
  std::cout << "║  3.  Them ket noi                               ║\n";
  std::cout << "║  4.  Xoa nguoi dung                             ║\n";
  std::cout << "║  5.  Xoa ket noi                                ║\n";
  std::cout << "║  6.  Hien thi danh sach nguoi dung              ║\n";
  std::cout << "║  7.  Xem thong tin nguoi dung                   ║\n";
  std::cout << "║  8.  Tim kiem nguoi dung theo ten               ║\n";
  std::cout << "║  9.  Xem ban be truc tiep                       ║\n";
  std::cout << "║ 10.  Tim ban cua ban (BFS)                      ║\n";
  std::cout << "║ 11.  Goi y ket ban                              ║\n";
  std::cout << "║ 12.  Thong ke do thi                            ║\n";
  std::cout << "║ 13.  Export ket qua ra file                     ║\n";
  std::cout << "║ 14.  Do hieu suat                               ║\n";
  std::cout << "║  0.  Thoat                                      ║\n";
  std::cout << "╚═════════════════════════════════════════════════╝\n";
}

int main() {
  #ifdef _WIN32
  SetConsoleOutputCP(CP_UTF8);
  #endif
  SocialMedia network;
  bool running = true;

  std::cout << "Chao mung den voi ung dung Mo phong Mang Xa Hoi!\n";
  std::cout << "Su dung BFS de tim \"nguoi quen cua nguoi quen\" va goi y ket "
               "ban.\n";

  while (running) {
    printMenu();
    int choice = readInt("Lua chon cua ban: ");
    clearInput(); // Xóa newline còn lại

    switch (choice) {
    case 0: {
      std::cout << "Tam biet!\n";
      running = false;
      break;
    }

    case 1: {
      std::string userFile =
          readLine("Nhap duong dan file users (vd: users.csv): ");
      std::string edgeFile =
          readLine("Nhap duong dan file edges (vd: edges.txt): ");
      bool ok1 = network.loadUsersFromFile(userFile);
      bool ok2 = network.loadConnectionsFromFile(edgeFile);
      if (ok1 && ok2) {
        std::cout << "[OK] Tai du lieu thanh cong! " << network.getUserCount()
                  << " nguoi dung, " << network.getEdgeCount() << " ket noi.\n";
      } else {
        std::cerr << "[LOI] Khong the tai du lieu!\n";
      }
      break;
    }

    case 2: {
      int id = readInt("Nhap User ID: ");
      clearInput();
      std::string name = readLine("Nhap ten: ");
      network.addUser(id, name);
      std::cout << "[OK] Da them nguoi dung " << name << " (ID: " << id
                << ").\n";
      break;
    }

    case 3: {
      int id1 = readInt("Nhap User ID 1: ");
      int id2 = readInt("Nhap User ID 2: ");
      network.addConnection(id1, id2);
      break;
    }

    case 4: {
      int id = readInt("Nhap User ID can xoa: ");
      network.removeUser(id);
      break;
    }

    case 5: {
      int id1 = readInt("Nhap User ID 1: ");
      int id2 = readInt("Nhap User ID 2: ");
      network.removeConnection(id1, id2);
      break;
    }

    case 6: {
      network.listUsers();
      break;
    }

    case 7: {
      int id = readInt("Nhap User ID: ");
      network.printUserInfo(id);
      break;
    }

    case 8: {
      std::string keyword = readLine("Nhap tu khoa tim kiem: ");
      Vector<int> results = network.searchUserByName(keyword);
      if (results.empty()) {
        std::cout << "\n[Thong bao] Khong tim thay nguoi dung nao phu hop!\n";
      } else {
        std::cout << "\n[OK] Tim thay " << results.size() << " nguoi dung phu hop:\n";
        for (size_t i = 0; i < results.size(); ++i) {
          network.printUserInfo(results[i]);
        }
      }
      break;
    }

    case 9: {
      int id = readInt("Nhap User ID: ");
      if (!network.userExists(id)) {
        std::cerr << "[LOI] Nguoi dung khong ton tai!\n";
        break;
      }
      HashSet<int> friends = network.getDirectConnections(id);
      std::cout << "\nBan be truc tiep cua " << network.getUserName(id)
                << " (ID: " << id << "): " << friends.size() << " nguoi\n";
      friends.forEach([&](int fid) {
        std::cout << "  " << fid << " - " << network.getUserName(fid) << "\n";
      });
      break;
    }

    case 10: {
      int id = readInt("Nhap User ID: ");
      if (!network.userExists(id)) {
        std::cerr << "[LOI] Nguoi dung khong ton tai!\n";
        break;
      }
      HashSet<int> fof = network.getFriendsOfFriends(id);
      Vector<int> fofVector = fof.toVector();
      Sort::sort(fofVector);

      size_t totalFoF = fofVector.size();
      if (totalFoF == 0) {
        std::cout << "\n[Thong bao] Nguoi dung nay khong co \"ban cua ban\"!\n";
        break;
      }

      size_t pageSize = 50;
      size_t totalPages = (totalFoF + pageSize - 1) / pageSize;
      size_t currentPage = 0;

      while (true) {
        std::cout << "\n==================================================\n";
        std::cout << "        BAN CUA BAN (BFS, Do sau 2) cua:\n";
        std::cout << "  " << network.getUserName(id) << " (ID: " << id << ")\n";
        std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages 
                  << " (Hien thi " << (currentPage * pageSize + 1) << " - " 
                  << std::min((currentPage + 1) * pageSize, totalFoF) << " / " << totalFoF << " nguoi)\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(12) << "ID" << "Ten\n";
        std::cout << "--------------------------------------------------\n";

        size_t start = currentPage * pageSize;
        size_t end = start + pageSize;
        if (end > totalFoF) end = totalFoF;

        for (size_t i = start; i < end; ++i) {
          int fid = fofVector[i];
          std::string fname = network.userExists(fid) ? network.getUserName(fid) : "User co lap";
          std::cout << "  " << std::left << std::setw(6) << (i + 1)
                    << std::setw(12) << fid
                    << fname << "\n";
        }

        std::cout << "--------------------------------------------------\n";
        std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve menu chinh\n";
        std::cout << "Lua chon cua ban: ";
        std::string choice;
        std::getline(std::cin, choice);
        if (choice == "n" || choice == "N") {
          if (currentPage + 1 < totalPages) {
            currentPage++;
          } else {
            std::cout << "[Thong bao] Da o trang cuoi cung!\n";
          }
        } else if (choice == "p" || choice == "P") {
          if (currentPage > 0) {
            currentPage--;
          } else {
            std::cout << "[Thong bao] Da o trang dau tien!\n";
          }
        } else {
          break;
        }
      }
      break;
    }

    case 11: {
      int id = readInt("Nhap User ID: ");
      int maxN = readInt("So luong goi y toi da: ");
      network.printSuggestions(id, maxN);
      break;
    }

    case 12: {
      network.printGraphStats();
      break;
    }

    case 13: {
      std::cout << "\n";
      std::cout << "╔═════════════════════════════════════════════════╗\n";
      std::cout << "║               EXPORT KET QUA RA FILE            ║\n";
      std::cout << "╠═════════════════════════════════════════════════╣\n";
      std::cout << "║  1. Export danh sach goi y ket ban              ║\n";
      std::cout << "║  2. Export bao cao thong ke do thi              ║\n";
      std::cout << "║  3. Export chi tiet thong tin & ban be user     ║\n";
      std::cout << "║  0. Quay lai menu chinh                         ║\n";
      std::cout << "╚═════════════════════════════════════════════════╝\n";
      int exportChoice = readInt("Lua chon export cua ban: ");
      clearInput();

      if (exportChoice == 0) break;

      switch (exportChoice) {
      case 1: {
        int id = readInt("Nhap User ID: ");
        int maxN = readInt("So luong goi y toi da: ");
        clearInput();
        std::string filepath =
            readLine("Nhap ten file xuat (vd: suggestions.txt): ");
        if (network.exportSuggestions(id, maxN, filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath << "\n";
        }
        break;
      }
      case 2: {
        std::string filepath = readLine("Nhap ten file xuat (vd: stats.txt): ");
        if (network.exportGraphStats(filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath << "\n";
        }
        break;
      }
      case 3: {
        int id = readInt("Nhap User ID: ");
        clearInput();
        std::string filepath =
            readLine("Nhap ten file xuat (vd: user_info.txt): ");
        if (network.exportUserConnections(id, filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath << "\n";
        }
        break;
      }
      default:
        std::cout << "[LOI] Lua chon khong hop le!\n";
        break;
      }
      break;
    }

    case 14: {
      int id = readInt("Nhap User ID de do hieu suat: ");
      network.measurePerformance(id);
      break;
    }

    default:
      std::cout << "[LOI] Lua chon khong hop le!\n";
      break;
    }
  }

  return 0;
}
