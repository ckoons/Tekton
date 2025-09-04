/*
 * tekton-clean-launch.c - Clean environment launcher for Tekton
 * 
 * This launcher handles environment setup before Python starts, avoiding
 * all the module import timing issues. Similar to how Git, Docker, and
 * other tools use compiled launchers.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <libgen.h>
#include <time.h>
#include <ctype.h>

#define MAX_PATH 4096
#define MAX_LINE 8192
#define MAX_ARGS 1024
#define TILL_REGISTRY_FILE ".till/tekton/till-private.json"

/* Structure to hold environment variables */
typedef struct {
    char **vars;
    int count;
    int capacity;
} env_list_t;

/* Function prototypes */
static char* find_tekton_root(const char *path_or_name);
static char* lookup_in_till_registry(const char *name);
static char* find_default_tekton(void);
static int is_tekton_directory(const char *path);
static int is_subcommand(const char *arg);
static void load_env_file(const char *filepath, env_list_t *env);
static void set_environment(env_list_t *env);
static char* get_env_value(env_list_t *env, const char *key);
static void parse_arguments(int argc, char *argv[], char **path_or_name, char **coder_letter, char **subcommand, char ***sub_args, int *debug);
static void execute_python_script(const char *script_name, char **args);
static void execute_till(char **args);
static env_list_t* create_env_list(void);
static void add_env_var(env_list_t *env, const char *key, const char *value);
static void write_javascript_env(const char *tekton_root, env_list_t *env);

int main(int argc, char *argv[]) {
    char *tekton_root;
    char *path_or_name = NULL;
    char *coder_letter = NULL;
    char *subcommand = NULL;
    char **sub_args = NULL;
    int debug = 0;
    env_list_t *env;
    char path[MAX_PATH];
    
    /* Parse arguments to find path/name and global options */
    parse_arguments(argc, argv, &path_or_name, &coder_letter, &subcommand, &sub_args, &debug);
    
    /* Handle 'tekton till' pass-through first */
    if (subcommand && strcmp(subcommand, "till") == 0) {
        execute_till(sub_args);
        return 1; /* Should not reach here */
    }
    
    /* Find TEKTON_ROOT using new resolution logic */
    /* Priority: coder_letter > path_or_name > current_dir > default */
    if (coder_letter) {
        /* Legacy -c flag support */
        char coder_name[32];
        snprintf(coder_name, sizeof(coder_name), "coder-%c", tolower(coder_letter[0]));
        tekton_root = lookup_in_till_registry(coder_name);
        if (!tekton_root) {
            fprintf(stderr, "Error: Coder-%c not found in registry\n", coder_letter[0]);
            return 1;
        }
    } else {
        tekton_root = find_tekton_root(path_or_name);
    }
    
    if (!tekton_root) {
        fprintf(stderr, "Error: Could not determine Tekton directory\n");
        fprintf(stderr, "Try 'tekton status' in a Tekton directory or specify a path\n");
        return 1;
    }
    
    /* Create environment list starting with current environment */
    env = create_env_list();
    
    /* Load environment files in order */
    /* 1. User home .env */
    snprintf(path, sizeof(path), "%s/.env", getenv("HOME"));
    load_env_file(path, env);
    
    /* 2. TEKTON_ROOT/.env.tekton */
    snprintf(path, sizeof(path), "%s/.env.tekton", tekton_root);
    load_env_file(path, env);
    
    /* 3. TEKTON_ROOT/.env.local */
    snprintf(path, sizeof(path), "%s/.env.local", tekton_root);
    load_env_file(path, env);
    
    /* Set the frozen environment marker */
    add_env_var(env, "_TEKTON_ENV_FROZEN", "1");
    
    /* Write env.js file for Hephaestus to read */
    write_javascript_env(tekton_root, env);

    /* Set debug logging if requested */
    if (debug) {
        add_env_var(env, "TEKTON_DEBUG", "1");
        add_env_var(env, "DEBUG", "1");
    }
    
    /* Apply all environment variables */
    set_environment(env);
    
    /* Handle help - show help if no subcommand or help requested */
    if (!subcommand || strcmp(subcommand, "help") == 0 || 
        strcmp(subcommand, "--help") == 0 || strcmp(subcommand, "-h") == 0) {
        printf("Usage: tekton [path-or-name] [command] [args...]\n");
        printf("       tekton [command] [path-or-name] [args...]\n\n");
        printf("Path/Name resolution:\n");
        printf("  path-or-name          Path to Tekton dir or registry name\n");
        printf("                        If omitted, uses current dir or default\n\n");
        printf("Global options:\n");
        printf("  -c, --coder <letter>  Use Coder-<letter> environment (legacy)\n");
        printf("  -d, --debug           Enable debug logging\n");
        printf("  -h, --help            Show this help message\n\n");
        printf("Commands:\n");
        printf("  status                Show component status\n");
        printf("  start, launch         Start components\n");
        printf("  stop, kill            Stop components\n");
        printf("  revert                Revert changes\n");
        printf("  till [args...]        Pass through to till command\n");
        printf("  help                  Show this help message\n\n");
        printf("Examples:\n");
        printf("  tekton start                    # Start Tekton in current dir\n");
        printf("  tekton start coder-b            # Start Coder-B from registry\n");
        printf("  tekton start /path/to/tekton   # Start specific path\n");
        printf("  tekton -c d status              # Status of Coder-D (legacy)\n");
        printf("  tekton till install tekton -i  # Run till interactively\n");
        return 0;
    }
    
    /* Route to appropriate Python script */
    if (strcmp(subcommand, "status") == 0) {
        execute_python_script("enhanced_tekton_status.py", sub_args);
    } else if (strcmp(subcommand, "start") == 0 || strcmp(subcommand, "launch") == 0) {
        execute_python_script("enhanced_tekton_launcher.py", sub_args);
    } else if (strcmp(subcommand, "stop") == 0 || strcmp(subcommand, "kill") == 0) {
        execute_python_script("enhanced_tekton_killer.py", sub_args);
    } else if (strcmp(subcommand, "revert") == 0) {
        execute_python_script("tekton-revert", sub_args);
    } else {
        fprintf(stderr, "Unknown command: %s\n", subcommand);
        fprintf(stderr, "Available commands: status, start, stop, revert\n");
        return 1;
    }
    
    /* Should not reach here */
    return 1;
}

static char* find_tekton_root(const char *path_or_name) {
    char resolved[MAX_PATH];
    
    /* Priority 1: Explicit path argument */
    if (path_or_name && (strchr(path_or_name, '/') || path_or_name[0] == '.')) {
        /* It's a path - verify it's a Tekton directory */
        if (is_tekton_directory(path_or_name)) {
            if (realpath(path_or_name, resolved)) {
                return strdup(resolved);
            }
        }
        return NULL;
    }
    
    /* Priority 2: Registry name lookup */
    if (path_or_name) {
        char *registry_path = lookup_in_till_registry(path_or_name);
        if (registry_path) {
            return registry_path;
        }
    }
    
    /* Priority 3: Current directory */
    if (is_tekton_directory(".")) {
        if (getcwd(resolved, sizeof(resolved))) {
            return strdup(resolved);
        }
    }
    
    /* Priority 4: Default Tekton */
    return find_default_tekton();
}

static int is_tekton_directory(const char *path) {
    char test_path[MAX_PATH];
    struct stat st;
    
    snprintf(test_path, sizeof(test_path), "%s/.env.tekton", path);
    if (stat(test_path, &st) == 0) {
        return 1;
    }
    return 0;
}

static int is_subcommand(const char *arg) {
    const char *commands[] = {
        "status", "start", "launch", "stop", "kill", 
        "revert", "till", "help", "--help", "-h",
        NULL
    };
    
    for (int i = 0; commands[i]; i++) {
        if (strcmp(arg, commands[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

static char* find_default_tekton(void) {
    char resolved[MAX_PATH];
    
    /* Try environment variable first for backwards compatibility */
    char *env_root = getenv("TEKTON_ROOT");
    if (env_root && is_tekton_directory(env_root)) {
        return strdup(env_root);
    }
    
    /* Look for primary.tekton.development.us in registry */
    char *primary = lookup_in_till_registry("primary");
    if (primary) {
        return primary;
    }
    
    /* Try ../Tekton relative to current directory */
    if (is_tekton_directory("../Tekton")) {
        if (realpath("../Tekton", resolved)) {
            return strdup(resolved);
        }
    }
    
    return NULL;
}

static char* lookup_in_till_registry(const char *name) {
    char till_path[MAX_PATH];
    char *home = getenv("HOME");
    FILE *fp;
    char line[MAX_LINE];
    char *result = NULL;
    int in_installations = 0;
    char current_key[256] = "";
    char lowercase_name[256];
    
    if (!home) return NULL;
    
    /* Convert name to lowercase for matching */
    int i;
    for (i = 0; name[i] && i < 255; i++) {
        lowercase_name[i] = tolower(name[i]);
    }
    lowercase_name[i] = '\0';
    
    /* Try .till symlink first */
    if (readlink(".till", till_path, sizeof(till_path)) > 0) {
        till_path[sizeof(till_path)-1] = '\0';
        strncat(till_path, "/tekton/till-private.json", 
                sizeof(till_path) - strlen(till_path) - 1);
    } else {
        /* Use default location */
        snprintf(till_path, sizeof(till_path), 
                 "%s/.till/tekton/till-private.json", home);
    }
    
    fp = fopen(till_path, "r");
    if (!fp) return NULL;
    
    /* Simple JSON parsing - look for installations section */
    while (fgets(line, sizeof(line), fp)) {
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        
        /* Check if we're in installations section */
        if (strstr(p, "\"installations\"")) {
            in_installations = 1;
            continue;
        }
        
        if (in_installations) {
            /* Look for registry names as keys */
            char *quote1 = strchr(p, '"');
            if (quote1) {
                char *quote2 = strchr(quote1 + 1, '"');
                if (quote2) {
                    *quote2 = '\0';
                    strcpy(current_key, quote1 + 1);
                    
                    /* Convert key to lowercase for comparison */
                    char lowercase_key[256];
                    for (i = 0; current_key[i] && i < 255; i++) {
                        lowercase_key[i] = tolower(current_key[i]);
                    }
                    lowercase_key[i] = '\0';
                    
                    /* Check for match - partial or full */
                    if (strstr(lowercase_key, lowercase_name) == lowercase_key) {
                        /* Found a match - now get the root path */
                        while (fgets(line, sizeof(line), fp)) {
                            if (strstr(line, "\"root\"")) {
                                char *root_quote1 = strrchr(line, ':');
                                if (root_quote1) {
                                    root_quote1 = strchr(root_quote1, '"');
                                    if (root_quote1) {
                                        char *root_quote2 = strchr(root_quote1 + 1, '"');
                                        if (root_quote2) {
                                            *root_quote2 = '\0';
                                            result = strdup(root_quote1 + 1);
                                            break;
                                        }
                                    }
                                }
                            }
                            /* Stop if we hit the next installation */
                            if (strchr(line, '}')) break;
                        }
                        if (result) break;
                    }
                }
            }
        }
    }
    
    fclose(fp);
    return result;
}

static env_list_t* create_env_list(void) {
    env_list_t *env = malloc(sizeof(env_list_t));
    env->capacity = 100;
    env->count = 0;
    env->vars = malloc(sizeof(char*) * env->capacity);
    
    /* Copy current environment */
    extern char **environ;
    for (int i = 0; environ[i]; i++) {
        char *eq = strchr(environ[i], '=');
        if (eq) {
            *eq = '\0';
            add_env_var(env, environ[i], eq + 1);
            *eq = '=';
        }
    }
    
    return env;
}

static void add_env_var(env_list_t *env, const char *key, const char *value) {
    /* Check if key already exists */
    for (int i = 0; i < env->count; i++) {
        char *eq = strchr(env->vars[i], '=');
        if (eq) {
            *eq = '\0';
            int match = strcmp(env->vars[i], key) == 0;
            *eq = '=';
            if (match) {
                /* Replace existing value */
                free(env->vars[i]);
                char *new_var = malloc(strlen(key) + strlen(value) + 2);
                sprintf(new_var, "%s=%s", key, value);
                env->vars[i] = new_var;
                return;
            }
        }
    }
    
    /* Add new variable */
    if (env->count >= env->capacity - 1) {
        env->capacity *= 2;
        env->vars = realloc(env->vars, sizeof(char*) * env->capacity);
    }
    
    char *new_var = malloc(strlen(key) + strlen(value) + 2);
    sprintf(new_var, "%s=%s", key, value);
    env->vars[env->count++] = new_var;
    env->vars[env->count] = NULL;
}

static void load_env_file(const char *filepath, env_list_t *env) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) return;  /* File doesn't exist, skip */
    
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), fp)) {
        /* Skip empty lines and comments */
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '\n' || *p == '#') continue;
        
        /* Find the = sign */
        char *eq = strchr(p, '=');
        if (!eq) continue;
        
        /* Split key and value */
        *eq = '\0';
        char *key = p;
        char *value = eq + 1;
        
        /* Trim key */
        char *key_end = eq - 1;
        while (key_end > key && (*key_end == ' ' || *key_end == '\t')) key_end--;
        *(key_end + 1) = '\0';
        
        /* Trim value and remove quotes */
        char *val_end = value + strlen(value) - 1;
        while (val_end > value && (*val_end == '\n' || *val_end == ' ' || *val_end == '\t')) val_end--;
        *(val_end + 1) = '\0';
        
        if ((*value == '"' && *val_end == '"') || (*value == '\'' && *val_end == '\'')) {
            value++;
            *val_end = '\0';
        }
        
        /* Add to environment */
        add_env_var(env, key, value);
    }
    
    fclose(fp);
}

static void set_environment(env_list_t *env) {
    for (int i = 0; i < env->count; i++) {
        char *eq = strchr(env->vars[i], '=');
        if (eq) {
            *eq = '\0';
            setenv(env->vars[i], eq + 1, 1);
            *eq = '=';
        }
    }
}

static void parse_arguments(int argc, char *argv[], char **path_or_name, char **coder_letter, char **subcommand, char ***sub_args, int *debug) {
    int i;
    int subcommand_index = -1;
    int path_index = -1;
    
    /* Initialize outputs */
    *path_or_name = NULL;
    
    /* First pass: look for non-option arguments */
    for (i = 1; i < argc; i++) {
        if (argv[i][0] != '-') {
            /* Check if this is a value for a previous option */
            if (i > 1 && (strcmp(argv[i-1], "--coder") == 0 || strcmp(argv[i-1], "-c") == 0)) {
                continue;  /* This is a value for --coder/-c */
            }
            
            /* Check if it's a known subcommand */
            if (is_subcommand(argv[i])) {
                subcommand_index = i;
                *subcommand = argv[i];
                /* Check if next arg is path/name */
                if (i + 1 < argc && argv[i + 1][0] != '-' && !is_subcommand(argv[i + 1])) {
                    path_index = i + 1;
                    *path_or_name = argv[i + 1];
                }
                break;
            } else {
                /* It's a path/name before the command */
                path_index = i;
                *path_or_name = argv[i];
                /* Check if next arg is a subcommand */
                if (i + 1 < argc && is_subcommand(argv[i + 1])) {
                    subcommand_index = i + 1;
                    *subcommand = argv[i + 1];
                }
                break;
            }
        }
    }
    
    /* Process only global options (before subcommand) */
    int limit = (subcommand_index > 0) ? subcommand_index : argc;
    for (i = 1; i < limit; i++) {
        /* Check for --coder or -c */
        if ((strcmp(argv[i], "--coder") == 0 || strcmp(argv[i], "-c") == 0) && i + 1 < limit) {
            *coder_letter = argv[i + 1];
            i++;  /* Skip the next arg (the letter) */
            continue;
        }
        
        /* Check for --debug or -d */
        if (strcmp(argv[i], "--debug") == 0 || strcmp(argv[i], "-d") == 0) {
            *debug = 1;
            continue;
        }
        
        /* Check for help flags */
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            *subcommand = "help";
            return;  /* No need to process further */
        }
    }
    
    /* Collect subcommand arguments if we found a subcommand */
    if (subcommand_index > 0) {
        /* Create sub_args array with everything after the subcommand, excluding path_or_name */
        static char *sub_args_array[MAX_ARGS];
        int j = 0;
        for (i = subcommand_index + 1; i < argc; i++) {
            /* Skip the path/name argument if it's at this position */
            if (path_index == i) {
                continue;
            }
            sub_args_array[j++] = argv[i];
        }
        sub_args_array[j] = NULL;
        *sub_args = sub_args_array;
    }
}

static void execute_python_script(const char *script_name, char **args) {
    char script_path[MAX_PATH];
    char *tekton_root = getenv("TEKTON_ROOT");
    
    snprintf(script_path, sizeof(script_path), "%s/scripts/%s", tekton_root, script_name);
    
    /* Build argument array for execv */
    char *exec_args[MAX_ARGS];
    exec_args[0] = "python3";
    exec_args[1] = script_path;
    
    int i = 2;
    if (args) {
        while (*args && i < MAX_ARGS - 1) {
            exec_args[i++] = *args++;
        }
    }
    exec_args[i] = NULL;
    
    /* Execute Python script */
    execvp("python3", exec_args);
    
    /* If we get here, exec failed */
    perror("execvp");
    exit(1);
}


static char* get_env_value(env_list_t *env, const char *key) {
    for (int i = 0; i < env->count; i++) {
        char *eq = strchr(env->vars[i], '=');
        if (eq) {
            size_t key_len = eq - env->vars[i];
            if (strncmp(env->vars[i], key, key_len) == 0 && key[key_len] == '\0') {
                return eq + 1;
            }
        }
    }
    return NULL;
}

static void write_javascript_env(const char *tekton_root, env_list_t *env) {
    char filepath[MAX_PATH];
    FILE *fp;
    time_t now;
    char timestamp[64];
    
    /* Build the output file path */
    snprintf(filepath, sizeof(filepath), "%s/Hephaestus/ui/scripts/env.js", tekton_root);
    
    /* Open file for writing */
    fp = fopen(filepath, "w");
    if (!fp) {
        fprintf(stderr, "Warning: Could not write env.js file to %s: %s\n", filepath, strerror(errno));
        return;
    }
    
    /* Get current timestamp */
    time(&now);
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", localtime(&now));
    
    /* Write the JavaScript header */
    fprintf(fp, "/**\n");
    fprintf(fp, " * Environment variables for Tekton UI\n");
    fprintf(fp, " * AUTO-GENERATED by tekton launcher - DO NOT EDIT MANUALLY\n");
    fprintf(fp, " * Generated at: %s\n", timestamp);
    fprintf(fp, " * \n");
    fprintf(fp, " * This file is automatically regenerated when Tekton starts.\n");
    fprintf(fp, " * Port values are read from the environment configuration.\n");
    fprintf(fp, " */\n\n");
    
    fprintf(fp, "console.log('[FILE_TRACE] Loading: env.js');\n\n");
    fprintf(fp, "// Single Port Architecture environment variables - from actual environment\n");
    
    /* Write port variables */
    fprintf(fp, "window.HEPHAESTUS_PORT = %s;  // Hephaestus port\n", get_env_value(env, "HEPHAESTUS_PORT") ?: "8080");
    fprintf(fp, "window.ENGRAM_PORT = %s;      // Engram port\n", get_env_value(env, "ENGRAM_PORT") ?: "8000");
    fprintf(fp, "window.HERMES_PORT = %s;      // Hermes port\n", get_env_value(env, "HERMES_PORT") ?: "8001");
    fprintf(fp, "window.ERGON_PORT = %s;       // Ergon port\n", get_env_value(env, "ERGON_PORT") ?: "8002");
    fprintf(fp, "window.RHETOR_PORT = %s;      // Rhetor port\n", get_env_value(env, "RHETOR_PORT") ?: "8003");
    fprintf(fp, "window.TERMA_PORT = %s;       // Terma port\n", get_env_value(env, "TERMA_PORT") ?: "8004");
    fprintf(fp, "window.ATHENA_PORT = %s;      // Athena port\n", get_env_value(env, "ATHENA_PORT") ?: "8005");
    fprintf(fp, "window.PROMETHEUS_PORT = %s;  // Prometheus port\n", get_env_value(env, "PROMETHEUS_PORT") ?: "8006");
    fprintf(fp, "window.HARMONIA_PORT = %s;    // Harmonia port\n", get_env_value(env, "HARMONIA_PORT") ?: "8007");
    fprintf(fp, "window.TELOS_PORT = %s;       // Telos port\n", get_env_value(env, "TELOS_PORT") ?: "8008");
    fprintf(fp, "window.SYNTHESIS_PORT = %s;   // Synthesis port\n", get_env_value(env, "SYNTHESIS_PORT") ?: "8009");
    fprintf(fp, "window.TEKTON_CORE_PORT = %s; // Tekton Core port\n", get_env_value(env, "TEKTON_CORE_PORT") ?: "8010");
    fprintf(fp, "window.METIS_PORT = %s;       // Metis port\n", get_env_value(env, "METIS_PORT") ?: "8011");
    fprintf(fp, "window.APOLLO_PORT = %s;      // Apollo port\n", get_env_value(env, "APOLLO_PORT") ?: "8012");
    fprintf(fp, "window.BUDGET_PORT = %s;      // Budget port\n", get_env_value(env, "BUDGET_PORT") ?: "8013");
    fprintf(fp, "window.PENIA_PORT = %s;       // Penia port (same as budget)\n", get_env_value(env, "PENIA_PORT") ?: "8013");
    fprintf(fp, "window.SOPHIA_PORT = %s;      // Sophia port\n", get_env_value(env, "SOPHIA_PORT") ?: "8014");
    fprintf(fp, "window.NOESIS_PORT = %s;      // Noesis port\n", get_env_value(env, "NOESIS_PORT") ?: "8015");
    fprintf(fp, "window.NUMA_PORT = %s;        // Numa port\n", get_env_value(env, "NUMA_PORT") ?: "8016");
    fprintf(fp, "window.AISH_PORT = %s;        // aish port\n", get_env_value(env, "AISH_PORT") ?: "8017");
    fprintf(fp, "window.AISH_MCP_PORT = %s;    // aish MCP port\n\n", get_env_value(env, "AISH_MCP_PORT") ?: "8018");
    
    /* Write port base configuration */
    fprintf(fp, "// Port base configuration for CI port calculation\n");
    fprintf(fp, "window.TEKTON_PORT_BASE = %s;      // Component port base\n", get_env_value(env, "TEKTON_PORT_BASE") ?: "8000");
    fprintf(fp, "window.TEKTON_AI_PORT_BASE = %s;   // CI port base\n\n", get_env_value(env, "TEKTON_AI_PORT_BASE") ?: "45000");
    
    /* Write CI port calculation function */
    fprintf(fp, "// Function to calculate CI port from component port\n");
    fprintf(fp, "function getAIPort(componentPort) {\n");
    fprintf(fp, "    // CI port = AI_BASE + (component_port - COMPONENT_BASE)\n");
    fprintf(fp, "    return window.TEKTON_AI_PORT_BASE + (componentPort - window.TEKTON_PORT_BASE);\n");
    fprintf(fp, "}\n\n");
    
    /* Write convenience CI port variables */
    fprintf(fp, "// CI specialist ports (calculated)\n");
    fprintf(fp, "window.NUMA_AI_PORT = getAIPort(window.NUMA_PORT);           // numa-ci port\n");
    fprintf(fp, "window.ENGRAM_AI_PORT = getAIPort(window.ENGRAM_PORT);       // engram-ci port\n");
    fprintf(fp, "window.HERMES_AI_PORT = getAIPort(window.HERMES_PORT);       // hermes-ci port\n");
    fprintf(fp, "window.RHETOR_AI_PORT = getAIPort(window.RHETOR_PORT);       // rhetor-ci port\n");
    fprintf(fp, "window.TEKTON_CORE_AI_PORT = getAIPort(window.TEKTON_CORE_PORT); // tekton-core-ci port\n\n");
    
    /* Write debug settings */
    fprintf(fp, "// Debug settings\n");
    fprintf(fp, "window.TEKTON_DEBUG = '%s';        // Master switch for debug instrumentation\n", 
            get_env_value(env, "TEKTON_DEBUG") ?: "true");
    fprintf(fp, "window.TEKTON_LOG_LEVEL = '%s';   // Default log level\n\n", 
            get_env_value(env, "TEKTON_LOG_LEVEL") ?: "DEBUG");
    
    /* Write metadata */
    fprintf(fp, "// Mark that ports are from environment, not defaults\n");
    fprintf(fp, "window.PORTS_FROM_ENV = true;\n");
    fprintf(fp, "window.TEKTON_ENV_TIMESTAMP = '%s';\n\n", timestamp);
    
    /* Write update function for compatibility */
    fprintf(fp, "// Function to update port values from server - NO LONGER NEEDED\n");
    fprintf(fp, "function updatePortsFromServer() {\n");
    fprintf(fp, "    console.log('[ENV] updatePortsFromServer called but ports already loaded from environment');\n");
    fprintf(fp, "    console.log('[ENV] TEKTON_CORE_PORT =', window.TEKTON_CORE_PORT);\n");
    fprintf(fp, "    console.log('[ENV] Ports were loaded at:', window.TEKTON_ENV_TIMESTAMP);\n");
    fprintf(fp, "    \n");
    fprintf(fp, "    // Still dispatch event for compatibility\n");
    fprintf(fp, "    window.dispatchEvent(new CustomEvent('ports-updated'));\n");
    fprintf(fp, "}\n\n");
    
    /* Write footer */
    fprintf(fp, "// No need to wait for DOMContentLoaded - ports are already correct\n");
    fprintf(fp, "console.log('[ENV] Loaded port configuration from tekton launcher');\n");
    fprintf(fp, "console.log('[ENV] TEKTON_CORE_PORT =', window.TEKTON_CORE_PORT);\n");
    fprintf(fp, "console.log('[ENV] NUMA_PORT =', window.NUMA_PORT);\n");
    fprintf(fp, "console.log('[ENV] Environment timestamp:', window.TEKTON_ENV_TIMESTAMP);\n");
    
    fclose(fp);
    
    if (getenv("DEBUG")) {
        fprintf(stderr, "Wrote JavaScript environment file: %s\n", filepath);
    }
}

static void execute_till(char **args) {
    char till_path[MAX_PATH];
    char *home = getenv("HOME");
    
    if (!home) {
        fprintf(stderr, "Error: HOME environment variable not set\n");
        exit(1);
    }
    
    /* Build path to till executable */
    snprintf(till_path, sizeof(till_path), "%s/projects/github/till/till", home);
    
    /* Check if till exists */
    struct stat st;
    if (stat(till_path, &st) != 0 || !S_ISREG(st.st_mode)) {
        fprintf(stderr, "Error: till not found at %s\n", till_path);
        exit(1);
    }
    
    /* Build argument array for execv */
    char *exec_args[MAX_ARGS];
    exec_args[0] = till_path;
    
    int i = 1;
    if (args) {
        while (*args && i < MAX_ARGS - 1) {
            exec_args[i++] = *args++;
        }
    }
    exec_args[i] = NULL;
    
    /* Execute till */
    execv(till_path, exec_args);
    
    /* If we get here, exec failed */
    perror("execv");
    exit(1);
}
