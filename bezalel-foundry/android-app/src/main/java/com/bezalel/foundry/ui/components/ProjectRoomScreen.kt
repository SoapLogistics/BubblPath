package com.bezalel.foundry.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ProjectRoomScreen(projectName: String, objective: String) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "Project Room: $projectName")
        Card(modifier = Modifier.padding(top = 8.dp)) {
            Text(
                text = "Objective: $objective",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
