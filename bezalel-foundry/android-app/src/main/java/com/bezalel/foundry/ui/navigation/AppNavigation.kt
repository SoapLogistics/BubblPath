package com.bezalel.foundry.ui.navigation

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.windowsizeclass.WindowSizeClass
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.bezalel.foundry.ui.screens.*

enum class Screen(val route: String) {
    Projects("projects"),
    Agents("agents"),
    Clipboard("clipboard"),
    Files("files"),
    Servers("servers"),
    Reports("reports"),
    Notifications("notifications"),
    Tasks("tasks"),
    Documentation("documentation")
}

@Composable
fun AppNavigation(
    windowSizeClass: WindowSizeClass,
    navController: NavHostController = rememberNavController()
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route ?: Screen.Projects.route

    val isExpanded = windowSizeClass.widthSizeClass == WindowWidthSizeClass.Expanded

    Scaffold(
        bottomBar = {
            if (!isExpanded) {
                // Future: Bottom Navigation implementation for compact devices
            }
        }
    ) { innerPadding ->
        Row(modifier = Modifier.padding(innerPadding)) {
            if (isExpanded) {
                // Future: Navigation Rail or Permanent Drawer implementation for expanded devices
            }

            NavHost(
                navController = navController,
                startDestination = Screen.Projects.route,
                modifier = Modifier.weight(1f)
            ) {
                composable(Screen.Projects.route) { ProjectsScreen() }
                composable(Screen.Agents.route) { AgentsScreen() }
                composable(Screen.Clipboard.route) { ClipboardScreen() }
                composable(Screen.Files.route) { FilesScreen() }
                composable(Screen.Servers.route) { ServersScreen() }
                composable(Screen.Reports.route) { ReportsScreen() }
                composable(Screen.Notifications.route) { NotificationsScreen() }
                composable(Screen.Tasks.route) { TasksScreen() }
                composable(Screen.Documentation.route) { DocumentationScreen() }
            }
        }
    }
}
