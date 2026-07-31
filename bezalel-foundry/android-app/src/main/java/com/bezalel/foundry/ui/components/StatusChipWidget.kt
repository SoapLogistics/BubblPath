package com.bezalel.foundry.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun BFStatusChip(
    text: String,
    containerColor: Color = MaterialTheme.colorScheme.primaryContainer,
    contentColor: Color = MaterialTheme.colorScheme.onPrimaryContainer,
    modifier: Modifier = Modifier
) {
    Text(
        text = text,
        color = contentColor,
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(containerColor)
            .padding(horizontal = 12.dp, vertical = 6.dp),
        style = MaterialTheme.typography.labelSmall
    )
}
