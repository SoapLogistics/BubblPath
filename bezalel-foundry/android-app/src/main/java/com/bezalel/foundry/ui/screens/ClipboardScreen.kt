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
import com.bezalel.foundry.ui.components.BFCodeViewer
import com.bezalel.foundry.ui.components.BFStatusChip

@Composable
fun ClipboardScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        Text("Clipboard", style = MaterialTheme.typography.headlineMedium)

        BFCard(modifier = Modifier.padding(top = 16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                BFStatusChip(text = "Code Snippet", modifier = Modifier.padding(bottom = 8.dp))
                BFCodeViewer(code = "def hello():\n    print('world')")
            }
        }

        BFCard(modifier = Modifier.padding(top = 16.dp)) {
            Column(modifier = Modifier.padding(16.dp)) {
                BFStatusChip(text = "Markdown", containerColor = MaterialTheme.colorScheme.secondaryContainer, contentColor = MaterialTheme.colorScheme.onSecondaryContainer, modifier = Modifier.padding(bottom = 8.dp))
                Text("Here is a markdown snippet saved to the clipboard.")
            }
        }
    }
}
