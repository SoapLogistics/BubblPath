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
fun ServersScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        Text("Servers", style = MaterialTheme.typography.headlineMedium)

        BFCard(modifier = Modifier.padding(top = 16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Gateway Proxy", style = MaterialTheme.typography.titleMedium)
                Text("localhost:8000", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(top = 4.dp, bottom = 8.dp))
                BFStatusChip(text = "Healthy")
            }
        }
    }
}
