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

#define MAX_PATH 4096
#define MAX_LINE 8192
#define MAX_ARGS 1024

/* Structure to hold environment variables */
typedef struct {
    char **vars;
    int count;
    int capacity;
} env_list_t;

/* Function prototypes */
static char* find_tekton_root(void);
static void load_env_file(const char *filepath, env_list_t *env);
static void set_environment(env_list_t *env);
static char* get_env_value(env_list_t *env, const char *key);
static void parse_arguments(int argc, char *argv[], char **coder_letter, char **subcommand, char ***sub_args, int *debug);
static void execute_python_script(const char *script_name, char **args);
static env_list_t* create_env_list(void);
static void free_env_list(env_list_t *env);
static void add_env_var(env_list_t *env, const char *key, const char *value);

int main(int argc, char *argv[]) {
    char *tekton_root;
    char *coder_letter = NULL;
    char *subcommand = NULL;
    char **sub_args = NULL;
    int debug = 0;
    env_list_t *env;
    char path[MAX_PATH];
    
    /* Find TEKTON_ROOT */
    tekton_root = find_tekton_root();
    if (!tekton_root) {
        fprintf(stderr, "Error: TEKTON_ROOT environment variable not set\n");
        return 1;
    }
    
    /* Parse arguments to find global options */
    parse_arguments(argc, argv, &coder_letter, &subcommand, &sub_args, &debug);
    
    /* If --coder specified, verify and switch TEKTON_ROOT */
    if (coder_letter) {
        char coder_dir[MAX_PATH];
        char *parent = dirname(strdup(tekton_root));
        snprintf(coder_dir, sizeof(coder_dir), "%s/Coder-%c", parent, coder_letter[0]);
        
        /* Verify .env.local exists */
        snprintf(path, sizeof(path), "%s/.env.local", coder_dir);
        struct stat st;
        if (stat(path, &st) != 0) {
            fprintf(stderr, "Error: Coder-%c environment not found at %s\n", coder_letter[0], path);
            return 1;
        }
        
        /* Update TEKTON_ROOT */
        tekton_root = strdup(coder_dir);
        setenv("TEKTON_ROOT", tekton_root, 1);
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
        printf("Usage: tekton [options] [command] [args...]\n\n");
        printf("Global options:\n");
        printf("  -c, --coder <letter>  Use Coder-<letter> environment\n");
        printf("  -d, --debug           Enable debug logging\n");
        printf("  -h, --help            Show this help message\n\n");
        printf("Commands:\n");
        printf("  status                Show component status\n");
        printf("  start, launch         Start components\n");
        printf("  stop, kill            Stop components\n");
        printf("  revert                Revert changes\n");
        printf("  help                  Show this help message\n");
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

static char* find_tekton_root(void) {
    char *env_root = getenv("TEKTON_ROOT");
    if (env_root) {
        return env_root;
    }
    return NULL;
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

static void parse_arguments(int argc, char *argv[], char **coder_letter, char **subcommand, char ***sub_args, int *debug) {
    int i;
    int subcommand_index = -1;
    
    /* First, find the subcommand (first non-option argument) */
    for (i = 1; i < argc; i++) {
        if (argv[i][0] != '-') {
            /* Check if this is a value for a previous option */
            if (i > 1 && (strcmp(argv[i-1], "--coder") == 0 || strcmp(argv[i-1], "-c") == 0)) {
                continue;  /* This is a value for --coder/-c */
            }
            /* This is the subcommand */
            subcommand_index = i;
            *subcommand = argv[i];
            break;
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
    if (subcommand_index > 0 && subcommand_index + 1 < argc) {
        /* Create sub_args array with everything after the subcommand */
        static char *sub_args_array[MAX_ARGS];
        int j = 0;
        for (i = subcommand_index + 1; i < argc; i++) {
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

static void free_env_list(env_list_t *env) {
    for (int i = 0; i < env->count; i++) {
        free(env->vars[i]);
    }
    free(env->vars);
    free(env);
}