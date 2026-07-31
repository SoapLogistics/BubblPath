package com.bezalel.foundry

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import androidx.compose.ui.Modifier
import com.bezalel.foundry.ui.navigation.AppNavigation
import com.bezalel.foundry.ui.theme.BezalelFoundryTheme
import com.bezalel.foundry.ui.theme.ThemeMode

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val windowSizeClass = calculateWindowSizeClass(this)

            BezalelFoundryTheme(themeMode = ThemeMode.SYSTEM) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppNavigation(windowSizeClass = windowSizeClass)
                }
            }
        }
    }
}
