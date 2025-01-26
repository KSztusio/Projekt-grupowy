#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <vector>

using namespace std;

double string_to_double(string number);

int main(int argc, char* argv[]) {
    int k, columns_n, n1_n, n2_n, step;
    string file_name = "data.mat";
    if (argc > 1) {
        file_name = argv[1];
    }

    string b, name, type, x, y, columns, n1, n2, deadzone;
    fstream plik;
    fstream plikzap;
    plik.open(file_name, ios::in);
    plikzap.open("dane.txt", ios::out);

    if (plik.is_open() && plikzap.is_open()) {
        int j = 0;
        while (!plik.eof()) {
            getline(plik, b);
            if (b[0] == '#') {
                if (b.substr(2, 4) == "name") {
                    name = "";
                    for (int i = 8; i < b.length(); i++) {
                        name += b[i];

                    }
                }
            }
            if (name == "azimuthRaster") {
                if (b[0] == '#') {
                    if (b.substr(2, 8) == "columns:") {
                        columns = "";
                        for (int l = 11; l < b.length(); l++) {
                            columns += b[l];
                            columns_n = stod(columns);
                        }
                    }
                }
                else if (b[0] == ' ') {
                    k = 1;
                    n1 = n2 = "";
                    while (b[k] != ' ') {
                        n1 += b[k];
                        n1_n = string_to_double(n1);
                        k++;
                    }
                    k++;
                    while (b[k] != ' ') {
                        n2 += b[k];
                        n2_n = string_to_double(n2);
                        k++;
                    }
                    step = n2_n - n1_n;
                    name = "";
                    plikzap << "azimuth\n" << n1 << ' ' << step << ' ' << columns_n - 1 << '\n';

                }
            }
            else if (name == "distanceRaster") {
                if (b[0] == '#') {
                    if (b.substr(2, 8) == "columns:") {
                        columns = "";
                        for (int l = 11; l < b.length(); l++) {
                            columns += b[l];
                            columns_n = stod(columns);
                        }
                    }
                }
                else if (b[0] == ' ') {
                    k = 1;
                    n1 = n2 = "";
                    while (b[k] != ' ') {
                        n1 += b[k];
                        n1_n = stod(n1);
                        k++;
                    }
                    k++;
                    while (b[k] != ' ') {
                        n2 += b[k];
                        n2_n = stod(n2);
                        k++;
                    }
                    step = n2_n - n1_n;
                    name = "";
                    plikzap << "distance\n" << n1 << ' ' << step << ' ' << columns_n - 1 << '\n';

                }
            }
            else if (name == "deadZone") {
                if (b[0] >= 48 && b[0] <= 57) {
                    deadzone = b;
                    plikzap << "deadZone\n" << deadzone << '\n';
                }
            }
            else if (name == "signal") {
                break;
            }
        }
        plik.close();

        // signal
        string binary_file_name = "results.bin";

        ifstream signal_file(binary_file_name, ios::binary);
        vector<double> results;
        double value;

        int k = 0;
        while (signal_file.read(reinterpret_cast<char*>(&value), sizeof(double))) {
            if (k % 36 == 5)
                plikzap << value << "\n";
            k++;
        }

        plikzap.close();
    }
    return 0;
}

double string_to_double(string number) {
    if (number.empty()) {
        cerr << "Błąd: pusty ciąg w string_to_double!" << '\n';
        return 0; // lub rzuć wyjątek
    }
    string nnumber;
    long double new_number = 0;
    int j = 0, l = 0;
    int modifier = 1;
    if (number[0] == '-') {
        modifier = -1;
        l = 1;
    }
    for (int k = l; k < (7 < number.length() ? 5 : number.length()); k++) {
        nnumber += number[k];
    }
    while (nnumber[j] != '.' && j < nnumber.length()) {
        j++;
    }
    for (int k = j - 1; k >= 0; k--) {
        new_number += ((int(nnumber[k]) - 48) * exp(j - k - 1));

    }
    for (int k = j + 1; k < nnumber.length(); k++) {
        new_number += ((int(nnumber[k]) - 48) * exp(j - k));
    }
    new_number *= modifier;
    return new_number;
}
