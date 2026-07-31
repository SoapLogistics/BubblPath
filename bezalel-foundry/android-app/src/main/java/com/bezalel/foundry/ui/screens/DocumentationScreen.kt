package com.bezalel.foundry.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.bezalel.foundry.ui.components.BFCard
import com.bezalel.foundry.ui.components.BFStatusChip

@Composable
fun DocumentationScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        Text("Documentation", style = MaterialTheme.typography.headlineMedium)

        BFCard(modifier = Modifier.padding(top = 16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Architecture Overview", style = MaterialTheme.typography.titleMedium)
                Text("Provides a coherent operating environment across an Android application and a lightweight backend Gateway.", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = 4.dp, bottom = 8.dp))
                BFStatusChip(text = "Updated")
            }
        }
    }
}
