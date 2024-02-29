#include <iostream>
#include <vector>
#include <queue>
using namespace std;
int main(){
    int numSticks, numLines;
    cin >> numSticks >> numLines;
    vector<vector<int>> adjList(numSticks+1);
    vector<int> degree(numSticks + 1);
    for(int i = 0; i < numLines; i++){
        int stick1, stick2;
        cin >> stick1 >> stick2;
        degree[stick2]++;
        adjList[stick1].push_back(stick2);
    }
    queue<int> q;
    for(int i = 1; i <= numSticks; i++){
        if(degree[i] == 0){
            q.push(i);
        }
    }
    vector<int> completed;
    while(!q.empty()){
        int current = q.front();
        q.pop();
        completed.push_back(current);
        for(auto i : adjList[current]){
            degree[i]--;
            if(degree[i] == 0){
                q.push(i);
            }
        }
    }
    if(completed.size() == numSticks){
        for(auto i : completed){
            cout << i << endl;
        }
        
    }
    else{
        cout << "IMPOSSIBLE" << endl;
    }
    return 0;
}