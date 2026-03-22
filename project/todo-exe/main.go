package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"
    "strconv"
    "strings"
)

type Todo struct {
    Text string `json:"text"`
    Done bool   `json:"done"`
}

func dataPath() string {
    exe, err := os.Executable()
    if err != nil {
        return "todo-data.json"
    }
    return filepath.Join(filepath.Dir(exe), "todo-data.json")
}

func loadTodos(path string) []Todo {
    b, err := os.ReadFile(path)
    if err != nil {
        return []Todo{}
    }
    var todos []Todo
    if json.Unmarshal(b, &todos) != nil {
        return []Todo{}
    }
    return todos
}

func saveTodos(path string, todos []Todo) error {
    b, err := json.MarshalIndent(todos, "", "  ")
    if err != nil {
        return err
    }
    return os.WriteFile(path, b, 0644)
}

func printTodos(todos []Todo) {
    fmt.Println("\n=== Todo List ===")
    if len(todos) == 0 {
        fmt.Println("(empty)")
    }
    for i, t := range todos {
        mark := " "
        if t.Done {
            mark = "x"
        }
        fmt.Printf("%d. [%s] %s\n", i+1, mark, t.Text)
    }
    fmt.Println("\n1) Add  2) Toggle  3) Delete  4) Clear done  5) Exit")
}

func main() {
    path := dataPath()
    todos := loadTodos(path)
    in := bufio.NewReader(os.Stdin)

    for {
        printTodos(todos)
        fmt.Print("Select: ")
        choiceRaw, _ := in.ReadString('\n')
        choice := strings.TrimSpace(choiceRaw)

        switch choice {
        case "1":
            fmt.Print("Enter todo: ")
            text, _ := in.ReadString('\n')
            text = strings.TrimSpace(text)
            if text != "" {
                todos = append([]Todo{{Text: text, Done: false}}, todos...)
                _ = saveTodos(path, todos)
            }
        case "2":
            fmt.Print("Toggle item number: ")
            raw, _ := in.ReadString('\n')
            n, err := strconv.Atoi(strings.TrimSpace(raw))
            if err == nil && n >= 1 && n <= len(todos) {
                todos[n-1].Done = !todos[n-1].Done
                _ = saveTodos(path, todos)
            }
        case "3":
            fmt.Print("Delete item number: ")
            raw, _ := in.ReadString('\n')
            n, err := strconv.Atoi(strings.TrimSpace(raw))
            if err == nil && n >= 1 && n <= len(todos) {
                todos = append(todos[:n-1], todos[n:]...)
                _ = saveTodos(path, todos)
            }
        case "4":
            kept := todos[:0]
            for _, t := range todos {
                if !t.Done {
                    kept = append(kept, t)
                }
            }
            todos = kept
            _ = saveTodos(path, todos)
        case "5":
            fmt.Println("Bye")
            return
        default:
            fmt.Println("Invalid selection")
        }
    }
}
