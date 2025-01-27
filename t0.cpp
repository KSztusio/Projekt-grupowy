#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <thread>
#include <vector>
#include <mutex>

#define LICZBA_WATKOW 10 // TODO dynamiczny przydzal 2 * hc-1

using namespace std;

struct Result {
    double modulus;
};

double first_lines[LICZBA_WATKOW];


// Przetwarzanie fragmentu pliku
void process_file_chunk(fstream& file, streampos start, streampos end, int thread_id, vector<Result>& results) {
    file.seekg(start);
    string line, x, y;
    double xf, yf, w;
    int licznik = 0;
    bool first = true;

    // Cofanie kursora do początku linii 
    char ch;
    while (file.tellg() > 1) {
        file.seekg(-1, ios_base::cur);
        ch = file.get();
        if (ch == '\n') { break; }
        file.seekg(-1, ios_base::cur);
    }

    // Przetwarzanie fragmentu
    while (file.tellg() < end && getline(file, line)) {
        x.clear();
        y.clear();
        x = y = "";  // Czyszczenie tymczasowych stringów
        if (line.length() > 4 && line[1] == '(') {
            // Przetwarzanie linii z punktami (x, y)
            bool g = true;
            for (int i = 2; i < line.length() - 1; i++) {
                if (line[i] != ',') {
                    if (g) x += line[i];
                    else y += line[i];
                }
                else {
                    g = false;
                }
            }
            xf = stod(x);
            yf = stod(y);
            w = sqrt((xf * xf) + (yf * yf));
            results.push_back({w});
            if (first) {
                first = false;
                first_lines[thread_id] = w;
            }

            licznik++;
        }
    }
    //cout << thread_id << "         " << xf << " " << yf <<"   "<<line<< endl;

    // Sprawdzenie czy po koncu tego fragmentu jest poczatek kolejnego
    if (thread_id != LICZBA_WATKOW) {
        getline(file, line);
        x.clear();
        y.clear();
        x = y = "";  // Czyszczenie tymczasowych stringów
        if (line.length() > 4 && line[1] == '(') {
            // Przetwarzanie linii z punktami (x, y)
            bool g = true;
            for (int i = 2; i < line.length() - 1; i++) {
                if (line[i] != ',') {
                    if (g) x += line[i];
                    else y += line[i];
                }
                else {
                    g = false;
                }
            }
            xf = stod(x);
            yf = stod(y);
            w = sqrt((xf * xf) + (yf * yf));
        }
        if (w != first_lines[thread_id + 1]) {
            results.push_back({w});
        }

        // Odczyt ostatniego wektora - sprawdzenie duplikacji z kolejnym
        if (results.back().modulus == first_lines[thread_id + 1]) {
            results.pop_back(); // usuniecie ostatniego elementu
        }
    }
}

int main(int argc, char* argv[]) {
    //int tstart = clock();

    string file_name = "data.mat";
    if (argc > 1) {
        file_name = argv[1];
    }

    for (int i = 0; i < LICZBA_WATKOW; i++) {
        first_lines[i] = -1;
    }

    fstream plik(file_name, ios::in);

    // Znajdź punkt startowy danych (signal)
    string line;
    streampos signal_start = 0;
    while (getline(plik, line)) {
        if (line.find("signal") != string::npos) {
            getline(plik, line);
            getline(plik, line);
            getline(plik, line); // TODO

            signal_start = plik.tellg(); // Pozycja za znalezionym "signal"
            break;
        }
    }
    // Ustawienie punktu startowego w pliku
    plik.seekg(0, ios::end);
    streampos file_end = plik.tellg();
    streampos chunk_size = (file_end - signal_start) / LICZBA_WATKOW;

    vector<vector<Result>> thread_results(LICZBA_WATKOW);

    // Utwórz wątki
    vector<thread> threads;
    for (int i = 0; i < LICZBA_WATKOW; ++i) {
        streampos chunk_start = signal_start + i * chunk_size;
        streampos chunk_end = (i == LICZBA_WATKOW - 1) ? file_end : chunk_start + chunk_size;

        threads.emplace_back([&, chunk_start, chunk_end, i]() {
            fstream thread_file(file_name, ios::in);
            process_file_chunk(thread_file, chunk_start, chunk_end, i + 1, ref(thread_results[i]));
            });
    }

    // Czekanie na zakończenie wątków
    for (auto& thread : threads) {
        thread.join();
    }

    // Scalenie wyników
    vector<Result> final_results;
    for (const auto& thread_results : thread_results) {
        final_results.insert(final_results.end(), thread_results.begin(), thread_results.end());
    }


    // Zapis wyników do pliku
    string binary_file_name = "results.bin";
    ofstream output_file(binary_file_name, ios::binary | ios::trunc);

    for (const auto& res : final_results) {
        output_file.write(reinterpret_cast<const char*>(&res.modulus), sizeof(double));
    }
    output_file.close();
    
    return 0;
}
