package com.bezalel.foundry.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp

@Composable
fun BFCodeViewer(
    code: String,
    modifier: Modifier = Modifier
) {
    Text(
        text = code,
        fontFamily = FontFamily.Monospace,
        modifier = modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(16.dp),
        color = MaterialTheme.colorScheme.onSurfaceVariant
    )
}
