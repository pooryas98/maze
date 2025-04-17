package com.example.mazeapp;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Stack;

public class MazeGenerator {

    public static char[][] createMaze(int width, int height) {
        int gridHeight = 2 * height + 1;
        int gridWidth = 2 * width + 1;
        char[][] grid = new char[gridHeight][gridWidth];

        // Initialize grid with walls
        for (int i = 0; i < gridHeight; i++) {
            for (int j = 0; j < gridWidth; j++) {
                grid[i][j] = '#';
            }
        }

        Stack<Point> stack = new Stack<>();
        Random random = new Random();

        // Choose a random starting cell
        int startX = random.nextInt(width);
        int startY = random.nextInt(height);
        int cellX = 2 * startX + 1;
        int cellY = 2 * startY + 1;
        grid[cellY][cellX] = ' ';
        stack.push(new Point(cellX, cellY));

        while (!stack.isEmpty()) {
            Point current = stack.pop();
            int currentX = current.x;
            int currentY = current.y;

            List<Point> neighbors = new ArrayList<>();

            // Check neighbors (up, down, left, right)
            int[][] directions = {{0, -2}, {0, 2}, {-2, 0}, {2, 0}};
            for (int[] dir : directions) {
                int dx = dir[0];
                int dy = dir[1];
                int nextX = currentX + dx;
                int nextY = currentY + dy;

                if (nextY > 0 && nextY < gridHeight && nextX > 0 && nextX < gridWidth && grid[nextY][nextX] == '#') {
                    neighbors.add(new Point(nextX, nextY));
                }
            }

            if (!neighbors.isEmpty()) {
                stack.push(current); // Push current back in for backtracking
                Point next = neighbors.get(random.nextInt(neighbors.size()));
                int nextX = next.x;
                int nextY = next.y;

                int wallX = currentX + (nextX - currentX) / 2;
                int wallY = currentY + (nextY - currentY) / 2;
                grid[wallY][wallX] = ' ';
                grid[nextY][nextX] = ' ';
                stack.push(next);
            }
        }

        // Add entry and exit points
        grid[1][0] = ' ';
        grid[gridHeight - 2][gridWidth - 1] = ' ';

        return grid;
    }

    private static class Point {
        int x, y;
        public Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
    }
}
