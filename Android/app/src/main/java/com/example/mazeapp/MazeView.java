package com.example.mazeapp;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

public class MazeView extends View {

    private char[][] mazeGrid;
    private int cellSize = 20; // Default cell size
    private Paint wallPaint, pathPaint;

    public MazeView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }

    private void init() {
        wallPaint = new Paint();
        wallPaint.setColor(Color.BLACK);
        wallPaint.setStyle(Paint.Style.FILL);

        pathPaint = new Paint();
        pathPaint.setColor(Color.WHITE);
        pathPaint.setStyle(Paint.Style.FILL);
    }

    public void setMazeGrid(char[][] mazeGrid) {
        this.mazeGrid = mazeGrid;
        invalidate(); // Request redraw
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        if (mazeGrid == null) {
            return;
        }

        int rows = mazeGrid.length;
        int cols = mazeGrid[0].length;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                float x = j * cellSize;
                float y = i * cellSize;

                if (mazeGrid[i][j] == '#') {
                    canvas.drawRect(x, y, x + cellSize, y + cellSize, wallPaint);
                } else {
                    canvas.drawRect(x, y, x + cellSize, y + cellSize, pathPaint);
                }
            }
        }
    }
}
