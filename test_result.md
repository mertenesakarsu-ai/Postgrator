#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  PostgreSQL bağlantı hatası düzeltilmesi ve Demo Modu eklenmesi

backend:
  - task: "Demo Migration Endpoint"
    implemented: true
    working: true
    file: "backend/services/migration_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "run_demo_migration fonksiyonu eklendi. Simüle edilmiş 8 tablolu Northwind migration'ı içeriyor."
      - working: true
        agent: "testing"
        comment: "Demo migration endpoint başarıyla test edildi. POST /api/import/demo job ID döndürüyor, GET /api/jobs/{job_id} doğru status veriyor, 8 demo tablo (Customers, Orders, Products vb.) oluşturuluyor ve migration tamamlanıyor. Minor fix: Stage enum değerleri ve TableInfo/JobStats model alanları düzeltildi."
  
  - task: "Lazy Service Loading"
    implemented: true
    working: true
    file: "backend/services/migration_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "MSSQL/PostgreSQL servislerini sadece gerçek migration'da yüklemek için lazy loading eklendi. Bu sayede ODBC bağımlılığı demo modda hata vermez."

frontend:
  - task: "Demo Butonu Ekleme"
    implemented: true
    working: true
    file: "frontend/src/components/UploadForm.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Demo modu butonu eklendi. handleDemo fonksiyonu /api/import/demo endpoint'ini çağırıyor."
  
  - task: "Demo UI Stili"
    implemented: true
    working: true
    file: "frontend/src/components/UploadForm.css"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Demo butonu için mor gradient renk ve divider eklemesi yapıldı."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Demo Migration Endpoint test edilecek"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      PostgreSQL bağlantı hatası çözüldü. Container'da PostgreSQL kurulu olmadığı için demo modu eklendi.
      
      Yapılan Değişiklikler:
      1. Backend'e run_demo_migration fonksiyonu eklendi
      2. Simüle edilmiş 8 tablolu Northwind veritabanı migration'ı eklendi
      3. Frontend'e "Demo Modu İle Dene" butonu eklendi
      4. Lazy service loading ile ODBC bağımlılığı hatası çözüldü
      5. README.md güncellendi
      
      Demo modu PostgreSQL, MSSQL veya .bak dosyası gerektirmeden migration işlemini simüle eder.