package com.bezalel.foundry.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = PrimaryLight,
    onPrimary = OnPrimaryLight,
    primaryContainer = PrimaryContainerLight,
    onPrimaryContainer = OnPrimaryContainerLight,
    background = BackgroundLight,
    surface = SurfaceLight,
)

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryDark,
    onPrimary = OnPrimaryDark,
    primaryContainer = PrimaryContainerDark,
    onPrimaryContainer = OnPrimaryContainerDark,
    background = BackgroundDark,
    surface = SurfaceDark,
)

private val EInkColorScheme = lightColorScheme(
    primary = PrimaryEInk,
    onPrimary = OnPrimaryEInk,
    background = BackgroundEInk,
    surface = SurfaceEInk,
    onBackground = OnSurfaceEInk,
    onSurface = OnSurfaceEInk,
    primaryContainer = BackgroundEInk,
    onPrimaryContainer = OnSurfaceEInk,
    secondaryContainer = BackgroundEInk,
    onSecondaryContainer = OnSurfaceEInk
)

enum class ThemeMode {
    LIGHT, DARK, E_INK, SYSTEM
}

@Composable
fun BezalelFoundryTheme(
    themeMode: ThemeMode = ThemeMode.SYSTEM,
    content: @Composable () -> Unit
) {
    val darkTheme = isSystemInDarkTheme()
    val colorScheme = when (themeMode) {
        ThemeMode.LIGHT -> LightColorScheme
        ThemeMode.DARK -> DarkColorScheme
        ThemeMode.E_INK -> EInkColorScheme
        ThemeMode.SYSTEM -> if (darkTheme) DarkColorScheme else LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
