# Visual Assets Guide for PowerPoint Presentation

## Screenshots to Capture

### 1. Test Generation Console Output
**Command:** `py regenerate_tests.py`

**How to Capture:**
1. Open Command Prompt/PowerShell
2. Navigate to project directory
3. Run: `py regenerate_tests.py`
4. Wait for completion (shows [OK] for all 10 tests)
5. Select the console window
6. Press `Win + Shift + S` (Windows) or `Cmd + Shift + 4` (Mac)
7. Capture the entire output showing all 10 test generations

**What Should Be Visible:**
- DEBUG lines showing Python executable
- "Regenerating all test files using SimpleTestGenerator..."
- All 10 [OK] Generated TC-001 through TC-010
- "All test files regenerated successfully!" message

**File Name Suggestion:** `screenshot_test_generation.png`

---

### 2. Pytest Execution Results
**Command:** `py -m pytest generated_tests/ -v`

**How to Capture:**
1. Open Command Prompt/PowerShell
2. Navigate to project directory
3. Run: `py -m pytest generated_tests/ -v`
4. Wait for completion (shows 10 passed)
5. Capture the full pytest output

**What Should Be Visible:**
- "test session starts" header
- All 10 test cases with PASSED status
- Progress percentages (10%, 20%, ..., 100%)
- "10 passed in 0.19s" summary line

**File Name Suggestion:** `screenshot_pytest_results.png`

---

### 3. Generated Test File Example
**File:** `generated_tests/test_TC_001.py`

**How to Capture:**
1. Open `generated_tests/test_TC_001.py` in VS Code or text editor
2. Capture the first 35-40 lines
3. Ensure imports and class structure are visible

**What Should Be Visible:**
- File header with "Standalone Demo"
- Import statements (standalone_framework)
- Test class definition
- First few test methods
- Mock API calls

**File Name Suggestion:** `screenshot_test_file.png`

---

### 4. Project Directory Structure
**Location:** Project root folder

**How to Capture:**
1. Open File Explorer
2. Navigate to "Demo Project" folder
3. Arrange files to show key files clearly
4. Capture the directory view

**What Should Be Visible:**
- Key files: app.py, config.py, requirements.txt
- Demo files: run_demo.py, regenerate_tests.py
- Framework: standalone_framework.py, simple_test_generator.py
- Generated: generated_tests/ folder
- Documentation: README.md, INSTALLATION.md, etc.

**File Name Suggestion:** `screenshot_directory_structure.png`

---

### 5. Framework Code Structure
**File:** `standalone_framework.py`

**How to Capture:**
1. Open `standalone_framework.py` in editor
2. Capture the class definitions
3. Show key methods and structure

**What Should Be Visible:**
- BaseTestCase class
- MockAPIClient class
- Key methods (get_product, create_product, etc.)
- Assertion utilities

**File Name Suggestion:** `screenshot_framework_code.png`

---

## Architecture Diagrams to Create

### Diagram 1: Multi-Agent Architecture
**Tools:** Draw.io, Lucidchart, PowerPoint SmartArt, or Visio

**Components to Include:**
```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
│    (Pipeline Coordination)             │
└──────┬────────────────────┬────────────┘
       │                    │
┌──────▼──────┐    ┌───────▼────────┐
│ QTest Agent │    │ Simple Test    │
│ (Fetch Test │    │ Generator      │
│  Cases)     │    │ (Generate Code)│
└─────────────┘    └───────┬────────┘
                          │
               ┌──────────▼─────────┐
               │ Test Executor      │
               │ Agent              │
               │ (Run Pytest)       │
               └──────────┬─────────┘
                          │
               ┌──────────▼─────────┐
               │ Fixer Agent       │
               │ (Analyze Failures)│
               └────────────────────┘
```

**Styling Tips:**
- Use different colors for each agent
- Add icons to represent each agent's function
- Show data flow arrows between agents
- Add labels for each agent's responsibility

**File Name Suggestion:** `architecture_multi_agent.png`

---

### Diagram 2: Test Generation Process Flow
**Tools:** PowerPoint shapes, Draw.io flowchart symbols

**Process Steps:**
```
Test Case Description
        ↓
   Extract Steps
        ↓
Identify Parameters
        ↓
Template Matching
        ↓
Code Generation
        ↓
Syntax Validation
        ↓
   Test File Output
```

**Styling Tips:**
- Use flowchart symbols (diamonds for decisions, rectangles for processes)
- Add decision points (e.g., "Template found?")
- Include error handling paths
- Use consistent color scheme

**File Name Suggestion:** `process_test_generation.png`

---

### Diagram 3: Standalone Framework Structure
**Tools:** UML class diagram tool, PowerPoint with boxes

**Classes to Show:**
```
┌─────────────────┐
│  BaseTestCase   │
├─────────────────┤
│ + setup_method()│
│ + log_step()    │
│ + api_client    │
│ + test_data     │
└─────────────────┘
         ↑
         │
┌─────────────────┐
│  TestTC_001     │
├─────────────────┤
│ + test_tc_001() │
│ - _product_id   │
└─────────────────┘

┌─────────────────┐
│  MockAPIClient  │
├─────────────────┤
│ + get_product() │
│ + create_product()│
│ + update_product()│
│ + search_products()│
└─────────────────┘
```

**Styling Tips:**
- Use UML notation (boxes for classes, arrows for inheritance)
- Show key methods and attributes
- Include relationship lines
- Add method signatures

**File Name Suggestion:** `architecture_framework.png`

---

### Diagram 4: Research Methodology Flowchart
**Tools:** PowerPoint SmartArt, Draw.io

**Phases:**
```
Problem Analysis
        ↓
  System Design
        ↓
 Implementation
        ↓
   Evaluation
        ↓
   Refinement
        ↓
  Final System
```

**Styling Tips:**
- Use chevron process flow
- Add icons for each phase
- Include iteration arrows (feedback loops)
- Add timeline indicators

**File Name Suggestion:** `methodology_flowchart.png`

---

### Diagram 5: OME Integration Architecture
**Tools:** Architecture diagram tool, PowerPoint

**Components:**
```
┌─────────────────┐
│  OME System     │
│  (Real API)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Test Automation│
│  System         │
├─────────────────┤
│ • Orchestrator  │
│ • Generator     │
│ • Executor      │
│ • Fixer         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Test Reports   │
└─────────────────┘
```

**Styling Tips:**
- Show OME as external system
- Highlight integration points
- Include authentication/security layers
- Add data flow indicators

**File Name Suggestion:** `architecture_ome_integration.png`

---

## PowerPoint Creation Tips

### Slide Design Best Practices:
1. **Consistent Theme:** Use same color scheme throughout
2. **Font Size:** Minimum 24pt for body text, 32pt for headers
3. **Visual Balance:** Balance text and images on each slide
4. **White Space:** Don't overcrowd slides
5. **Contrast:** Ensure text is readable against backgrounds

### Screenshot Placement:
- Place screenshots in center or right side
- Add borders/shadows for emphasis
- Include callouts/arrows to highlight key areas
- Add captions below screenshots

### Diagram Styling:
- Use professional colors (blues, grays, greens)
- Add subtle shadows for depth
- Ensure text is readable on diagrams
- Use consistent icon style

### Animation (Optional):
- Use simple fade-in for bullet points
- Animate process flows step-by-step
- Don't overuse animations (distracting)

---

## Image File Organization

Create a folder structure:
```
Demo Project/
├── presentation_images/
│   ├── screenshots/
│   │   ├── test_generation.png
│   │   ├── pytest_results.png
│   │   ├── test_file.png
│   │   ├── directory_structure.png
│   │   └── framework_code.png
│   └── diagrams/
│       ├── multi_agent_architecture.png
│       ├── test_generation_flow.png
│       ├── framework_structure.png
│       ├── methodology_flowchart.png
│       └── ome_integration.png
```

---

## Quick Capture Checklist

Before Presentation:
- [ ] All 5 screenshots captured
- [ ] All 5 architecture diagrams created
- [ ] Images organized in folders
- [ ] Screenshots are readable (not blurry)
- [ ] Diagrams have consistent styling
- [ ] File names are descriptive
- [ ] Images are high resolution
- [ ] Text in images is legible

---

## Alternative: Live Demo

**Consider doing a live demo instead of screenshots:**

**Setup:**
1. Open Command Prompt before presentation
2. Navigate to project directory
3. Have commands ready in a text file
4. Test the demo beforehand

**Live Demo Commands:**
```bash
# Show directory structure
dir /b

# Show dependencies
pip list

# Run demo
py run_demo.py
```

**Benefits:**
- More engaging for audience
- Shows real-time execution
- Demonstrates reliability
- Allows for questions during execution

**Risks:**
- Something could go wrong
- Takes more time
- Requires reliable environment

**Recommendation:** Have both screenshots (as backup) and be prepared for live demo if environment permits.

---

## Presentation Software Tips

### PowerPoint:
- Use "Slide Master" for consistent design
- Create custom color theme
- Use "SmartArt" for quick diagrams
- Use "Screenshot" tool for quick captures

### Google Slides:
- Easy collaboration
- Cloud-based access
- Built-in image editing
- Template gallery available

### Keynote (Mac):
- Professional templates
- Smooth animations
- Excellent for Apple ecosystem
- Easy iPhone remote control

Choose whatever you're most comfortable with - content matters more than tool!
