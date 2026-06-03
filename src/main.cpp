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
      std::cerr << "\n[LOI] Da het du lieu dau vao. Chuong trinh se thoat.\n";
      exit(0);
    }
    std::cerr << "[LOI] Gia tri khong hop le. Vui long nhap mot so nguyen.\n";
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
  std::cout << "║      MANG XA HOI - MO PHONG THUAT TOAN BFS      ║\n";
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

  std::cout << "Chao mung ban den voi chuong trinh Mo phong Mang Xa Hoi!\n";
  std::cout << "He thong su dung thuat toan BFS de tim ban cua ban va goi y "
               "ket ban.\n";

  while (running) {
    printMenu();
    int choice = readInt("Lua chon cua ban: ");
    clearInput(); // Xóa newline còn lại

    switch (choice) {
    case 0: {
      std::cout << "Cam on ban da su dung chuong trinh. Tam biet!\n";
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
        std::cout << "[OK] Tai du lieu thanh cong: " << network.getUserCount()
                  << " nguoi dung, " << network.getEdgeCount() << " ket noi.\n";
      } else {
        std::cerr << "[LOI] Tai du lieu that bai. Vui long kiem tra lai duong "
                     "dan file.\n";
      }
      break;
    }

    case 2: {
      int id = readInt("Nhap User ID: ");
      clearInput();
      std::string name = readLine("Nhap ten: ");
      if (network.addUser(id, name)) {
        std::cout << "[OK] Da them thanh cong nguoi dung \"" << name
                  << "\" voi ID " << id << ".\n";
      }
      break;
    }

    case 3: {
      int id1 = readInt("Nhap User ID 1: ");
      int id2 = readInt("Nhap User ID 2: ");
      if (network.addConnection(id1, id2)) {
        std::cout << "[OK] Da ket noi thanh cong: User ID " << id1
                  << " <-> User ID " << id2 << ".\n";
      }
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
      clearInput();
      network.printUserInfo(id);
      break;
    }

    case 8: {
      std::string keyword = readLine("Nhap tu khoa tim kiem: ");
      if (keyword.empty()) {
        std::cout << "\n[Thong bao] Vui long nhap tu khoa tim kiem.\n";
        break;
      }
      Vector<int> results = network.searchUserByName(keyword);
      if (results.empty()) {
        std::cout << "\n[Thong bao] Khong tim thay nguoi dung nao phu hop voi "
                     "tu khoa \""
                  << keyword << "\".\n";
        break;
      }
      // Sắp xếp kết quả theo ID
      Sort::sort(results, [](int a, int b) { return a < b; });
      size_t total = results.size();
      size_t pageSize = 20;
      size_t totalPages = (total + pageSize - 1) / pageSize;
      size_t currentPage = 0;
      while (true) {
        std::cout << "\n==================================================\n";
        std::cout << "        KET QUA TIM KIEM: \"" << keyword << "\"\n";
        std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
                  << " (Hien thi " << (currentPage * pageSize + 1) << " - "
                  << std::min((currentPage + 1) * pageSize, total) << " / "
                  << total << " nguoi)\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(8)
                  << "ID" << std::setw(25) << "Ten"
                  << "So ban be\n";
        std::cout << "--------------------------------------------------\n";
        size_t start = currentPage * pageSize;
        size_t end = std::min(start + pageSize, total);
        for (size_t i = start; i < end; ++i) {
          int uid = results[i];
          std::string uname = network.getUserName(uid);
          int friendCount = 0;
          const HashSet<int> *friends = network.getDirectConnections(uid);
          friendCount =
              friends != nullptr ? static_cast<int>(friends->size()) : 0;
          std::cout << "  " << std::left << std::setw(6) << (i + 1)
                    << std::setw(8) << uid << std::setw(25) << uname
                    << friendCount << "\n";
        }
        std::cout << "--------------------------------------------------\n";
        std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | "
                     "[Enter] Ve menu chinh\n";
        std::cout << "Chon hoac nhap ID nguoi dung de xem chi tiet: ";
        std::string nav;
        std::getline(std::cin, nav);
        if (nav == "n" || nav == "N") {
          if (currentPage + 1 < totalPages)
            currentPage++;
          else
            std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai "
                         "hoac [Enter] de thoat.\n";
        } else if (nav == "p" || nav == "P") {
          if (currentPage > 0)
            currentPage--;
          else
            std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang "
                         "tiep theo.\n";
        } else if (nav.empty()) {
          break;
        } else {
          // Thử parse ID để xem chi tiết
          try {
            int viewID = std::stoi(nav);
            if (network.userExists(viewID)) {
              network.printUserInfo(viewID);
            } else {
              std::cerr << "[LOI] Nguoi dung ID " << viewID
                        << " khong ton tai!\n";
            }
          } catch (...) {
            std::cerr << "[LOI] Lua chon khong hop le.\n";
          }
        }
      }
      break;
    }

    case 9: {
      int id = readInt("Nhap User ID: ");
      clearInput();
      if (!network.userExists(id)) {
        std::cerr << "[LOI] Nguoi dung voi ID " << id << " khong ton tai!\n";
        break;
      }
      const HashSet<int> *friends = network.getDirectConnections(id);
      if (friends == nullptr || friends->size() == 0) {
        std::cout << "\n[Thong bao] Nguoi dung nay chua co ban be nao.\n";
        break;
      }

      // Chuyen sang vector de phan trang
      Vector<int> friendList = friends->toVector();
      Sort::sort(friendList);

      size_t total = friendList.size();
      size_t pageSize = 20;
      size_t totalPages = (total + pageSize - 1) / pageSize;
      size_t currentPage = 0;

      while (true) {
        std::cout << "\n==================================================\n";
        std::cout << "       BAN BE TRUC TIEP CUA:\n";
        std::cout << "  " << network.getUserName(id) << " (ID: " << id << ")\n";
        std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
                  << " (Hien thi " << (currentPage * pageSize + 1) << " - "
                  << std::min((currentPage + 1) * pageSize, total) << " / "
                  << total << " nguoi)\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(12)
                  << "ID"
                  << "Ten\n";
        std::cout << "--------------------------------------------------\n";

        size_t start = currentPage * pageSize;
        size_t end = std::min(start + pageSize, total);
        for (size_t i = start; i < end; ++i) {
          int fid = friendList[i];
          std::string fname = network.getUserName(fid);
          if (fname.empty())
            fname = "User co lap";
          std::cout << "  " << std::left << std::setw(6) << (i + 1)
                    << std::setw(12) << fid << fname << "\n";
        }
        std::cout << "--------------------------------------------------\n";

        if (totalPages <= 1)
          break;

        std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve "
                     "menu chinh\n";
        std::cout << "Lua chon cua ban: ";
        std::string nav;
        std::getline(std::cin, nav);
        if (nav == "n" || nav == "N") {
          if (currentPage + 1 < totalPages)
            currentPage++;
          else
            std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai "
                         "hoac [Enter] de thoat.\n";
        } else if (nav == "p" || nav == "P") {
          if (currentPage > 0)
            currentPage--;
          else
            std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang "
                         "tiep theo.\n";
        } else {
          break;
        }
      }
      break;
    }

    case 10: {
      int id = readInt("Nhap User ID: ");
      clearInput();
      if (!network.userExists(id)) {
        std::cerr << "[LOI] Nguoi dung voi ID " << id << " khong ton tai!\n";
        break;
      }
      HashSet<int> fof = network.getFriendsOfFriends(id);
      Vector<int> fofVector = fof.toVector();
      Sort::sort(fofVector);

      size_t totalFoF = fofVector.size();
      if (totalFoF == 0) {
        std::cout << "\n[Thong bao] Nguoi dung nay chua co \"ban cua ban\" "
                     "trong mang.\n";
        break;
      }

      size_t pageSize = 20;
      size_t totalPages = (totalFoF + pageSize - 1) / pageSize;
      size_t currentPage = 0;

      while (true) {
        std::cout << "\n==================================================\n";
        std::cout << "        BAN CUA BAN (BFS, Do sau 2) cua:\n";
        std::cout << "  " << network.getUserName(id) << " (ID: " << id << ")\n";
        std::cout << "  Trang " << (currentPage + 1) << "/" << totalPages
                  << " (Hien thi " << (currentPage * pageSize + 1) << " - "
                  << std::min((currentPage + 1) * pageSize, totalFoF) << " / "
                  << totalFoF << " nguoi)\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "  " << std::left << std::setw(6) << "STT" << std::setw(12)
                  << "ID" << "Ten\n";
        std::cout << "--------------------------------------------------\n";

        size_t start = currentPage * pageSize;
        size_t end = start + pageSize;
        if (end > totalFoF)
          end = totalFoF;

        for (size_t i = start; i < end; ++i) {
          int fid = fofVector[i];
          std::string fname = network.userExists(fid) ? network.getUserName(fid)
                                                      : "User co lap";
          std::cout << "  " << std::left << std::setw(6) << (i + 1)
                    << std::setw(12) << fid << fname << "\n";
        }

        if (totalPages <= 1)
          break;

        std::cout << "--------------------------------------------------\n";
        std::cout << "Phim tat: [n] Trang sau | [p] Trang truoc | [Enter] Ve "
                     "menu chinh\n";
        std::cout << "Lua chon cua ban: ";
        std::string choice;
        std::getline(std::cin, choice);
        if (choice == "n" || choice == "N") {
          if (currentPage + 1 < totalPages) {
            currentPage++;
          } else {
            std::cout << "[Thong bao] Day la trang cuoi. Nhan [p] de quay lai "
                         "hoac [Enter] de thoat.\n";
          }
        } else if (choice == "p" || choice == "P") {
          if (currentPage > 0) {
            currentPage--;
          } else {
            std::cout << "[Thong bao] Day la trang dau. Nhan [n] de xem trang "
                         "tiep theo.\n";
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
      clearInput();
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

      if (exportChoice == 0)
        break;

      switch (exportChoice) {
      case 1: {
        int id = readInt("Nhap User ID: ");
        int maxN = readInt("So luong goi y toi da: ");
        clearInput();
        std::string filepath =
            readLine("Nhap ten file xuat (vd: suggestions.txt): ");
        if (network.exportSuggestions(id, maxN, filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath
                    << "\n";
        }
        break;
      }
      case 2: {
        std::string filepath = readLine("Nhap ten file xuat (vd: stats.txt): ");
        if (network.exportGraphStats(filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath
                    << "\n";
        }
        break;
      }
      case 3: {
        int id = readInt("Nhap User ID: ");
        clearInput();
        std::string filepath =
            readLine("Nhap ten file xuat (vd: user_info.txt): ");
        if (network.exportUserConnections(id, filepath)) {
          std::cout << "\n[OK] Xuat thanh cong! File ket qua: " << filepath
                    << "\n";
        }
        break;
      }
      default:
        std::cerr << "[LOI] Lua chon khong hop le. Vui long nhap lai (0-3).\n";
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
      std::cerr << "[LOI] Lua chon khong hop le. Vui long nhap lai (0-14).\n";
      break;
    }
  }

  return 0;
}
