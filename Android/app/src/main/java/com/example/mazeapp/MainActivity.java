package com.example.mazeapp;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private MazeView mazeView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mazeView = findViewById(R.id.mazeView);
        
        // Generate and display a maze
        int mazeWidth = 10;
        int mazeHeight = 10;
        char[][] maze = MazeGenerator.createMaze(mazeWidth, mazeHeight);
        mazeView.setMazeGrid(maze);
    }
}
