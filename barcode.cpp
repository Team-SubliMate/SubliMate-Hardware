#include <iostream>
#include <curl/curl.h>

using namespace std;

int main() {
	string input;
	while(true) {
		getline(cin, input);
		cout << input << endl;
	}
}
