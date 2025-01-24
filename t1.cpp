#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
using namespace std;
double string_to_double(string number);
float exp(int n);
int main(int argc, char* argv[]){
    int k, columns_n, n1_n, n2_n, step;
    string file_name = "data.mat";
    if (argc > 1) {
        file_name = argv[1];
    } 
    string b, name, type, x, y, columns, n1, n2, deadzone;
    double xf, yf, w;
    fstream plik;
    fstream plikzap;
    plik.open(file_name, ios::in);
    plikzap.open("dane.txt", ios::out);
    if (plik.is_open() && plikzap.is_open()){
        int j = 0;
        while(!plik.eof()){
            getline(plik, b);
            if(b[0] == '#'){
                if (b.substr(2,4) == "name"){
                    name = "";
                    for(int i = 8; i < b.length(); i++){
                        name += b[i];
                        
                    }
                }
            }
            if (name == "signal"){
                if (b.length() > 4){
                    if(b[1] == '('){
                        bool g = true;
                        for(int i = 2; i < b.length()-1; i++) {
                            if(b[i]!=','){
                                if(g){
                                    x += b[i];
                                }else{
                                    y += b[i];
                                }
                            }else{
                                g = false;
                            }   
                        }
                        if (j % 36 == 5){
                            xf = string_to_double(x);
                            yf = string_to_double(y);
                            w = sqrt((xf*xf)+(yf*yf));
                            plikzap << to_string(w) << '\n';
                        }
                        j++;
                        //cout << w << '\n';
                        x = "";
                        y = "";
                    }
                }
            } else if (name == "azimuthRaster"){
                if(b[0] == '#'){
                    if (b.substr(2,8) == "columns:"){
                        columns = "";
                        for (int l = 11; l < b.length(); l++){
                            columns += b[l];
                            columns_n = string_to_double(columns);
                        }
                    }
                }else if(b[0] == ' '){
                    k = 1;
                    n1 = n2 = "";
                    while(b[k] != ' '){
                        n1 += b[k];
                        n1_n = string_to_double(n1);
                        k++;
                    }
                    k++;
                    while(b[k] != ' '){
                        n2 += b[k];
                        n2_n = string_to_double(n2);
                        k++;
                    }
                    step = n2_n - n1_n;
                    name = "";
                    plikzap << "azimuth\n" << n1 << ' ' << step << ' ' << columns_n-1 << '\n';

                }
            }else if (name == "distanceRaster"){
                if(b[0] == '#'){
                    if (b.substr(2,8) == "columns:"){
                        columns = "";
                        for (int l = 11; l < b.length(); l++){
                            columns += b[l];
                            columns_n = string_to_double(columns);
                        }
                    }
                }else if(b[0] == ' '){
                    k = 1;
                    n1 = n2 = "";
                    while(b[k] != ' '){
                        n1 += b[k];
                        n1_n = string_to_double(n1);
                        k++;
                    }
                    k++;
                    while(b[k] != ' '){
                        n2 += b[k];
                        n2_n = string_to_double(n2);
                        k++;
                    }
                    step = n2_n - n1_n;
                    name = "";
                    plikzap << "distance\n" << n1 << ' ' << step << ' ' << columns_n-1 << '\n';

                }
            }else if (name == "deadZone"){
                if(b[0] >= 48 && b[0] <= 57){
                    deadzone = b;
                    plikzap << "deadZone\n" << deadzone << '\n'; 
                }
            }
        }
        plikzap.close();
        plik.close();
    }
    return 0;
}
double string_to_double(string number){
    if (number.empty()) {
        cerr << "Błąd: pusty ciąg w string_to_double!" << '\n';
        return 0; // lub rzuć wyjątek
    }
    string nnumber;
    long double new_number = 0;
    int j = 0, l = 0;
    int modifier = 1;
    if(number[0] == '-'){
        modifier = -1;
        l = 1;
    }
    for (int k = l; k < (7 < number.length()? 5: number.length()); k++){
        nnumber += number[k];
    }
    while(nnumber[j] != '.' && j < nnumber.length()){
        j++;
    }
    for (int k = j-1; k >= 0; k--){
        new_number += ((int(nnumber[k]) - 48) * exp(j - k - 1));
        
    }
    for (int k = j+1; k < nnumber.length(); k++){
        new_number += ((int(nnumber[k]) - 48) * exp(j - k));
    }
    new_number *= modifier;
    return new_number;
}
float exp(int n){
    float e = 1;
    if (n >= 0){
        for (int i = 0; i < n; i++){
            e *= 10;
        }
    }else{
        for (int i = 0; i < -n; i++){
            e *= 0.1;
        }
    }
    return e;
}