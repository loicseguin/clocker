#include <iostream>
#include <fstream>
#include <cstdlib>
#include <cstring>

using namespace std;

// Get the clocker file name.
const char* getClockerFileName() {
  const char* pPath;
  pPath = getenv("CLOCKER_FILE");
  if (pPath == NULL) {
    pPath = ".clocker";
  }
  return pPath;
}

// Get the clocker file for reading.
ifstream* getClockerInFile() {
  const char* pPath = getClockerFileName();
  ifstream* fin = new ifstream();
  fin->open(pPath);
  return fin;
}

// Get the clocker file for writing.
ofstream* getClockerOutFile() {
  const char* pPath = getClockerFileName();
  ofstream* fin = new ofstream();
  fin->open(pPath, ios::app);
  return fin;
}

// Get the last line of the clocker file.
string getLastLine() {
  ifstream* fin = getClockerInFile();
  string line = "";
  if (fin->is_open()) {
    while (*fin >> ws && getline(*fin, line))
      ;
    fin->close();
  }
  delete fin;
  return line;
}

// Read clocker file and determine if last entry is a clock in event. Return
// true if it is, false otherwise.
bool isClockedIn() {
  string line = getLastLine();
  if (line.find("IN") != string::npos) {
    return true;
  }
  return false;
}

// Print usage message.
void usage()
{
  cerr <<
      "usage: clocker [-h] [in, out, report]\n"
      "clocker records working durations between clock in and clock out events.\n\n"
      "Option\n"
      "------\n"
      "-h    Print this usage message and exit.\n\n"
      "Example\n"
      "-------\n"
      "Start the day by clocking in\n"
      "  $ clocker in\n"
      "Then, end the day by clocking out\n"
      "  $ clocker out\n"
      "At the end of the week, print a report of the hours worked\n"
      "  $ clocker report\n";

  exit(1);
}

// Record a clock in event in the clocker file.
void clockIn()
{
  if (isClockedIn()) {
    cerr << "ERROR: Already clocked in." << endl;
    return;
  }
  cout << "clocking in" << endl;
  ofstream* fout = getClockerOutFile();
  *fout << "clocking IN" << endl;
}

// Record a clock out event in the clocker file.
void clockOut()
{
  if (!isClockedIn()) {
    cerr << "ERROR: Not clocked in." << endl;
    return;
  }
  cout << "clocking out" << endl;
  ofstream* fout = getClockerOutFile();
  *fout << "clocking OUT" << endl;
}

void report()
{
  cout << "weekly report" << endl;
}

int main(int argc, char *argv[])
{
  if (argc != 2) {
    usage();
  }
  if (strncmp(argv[1], "-h", 2) == 0 || strncmp(argv[1], "--help", 6) == 0) {
    usage();
  }
  if (strncmp(argv[1], "in", 2) == 0) {
    clockIn();
  }
  else if (strncmp(argv[1], "out", 3) == 0) {
    clockOut();
  }
  else if (strncmp(argv[1], "report", 6) == 0) {
    report();
  }
  else {
    usage();
  }
  return 0;
}
