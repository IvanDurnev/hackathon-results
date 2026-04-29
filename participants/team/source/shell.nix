{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "ai-presentation-generator";
  
  buildInputs = with pkgs; [
    # Node.js and npm for frontend
    nodejs_20
    nodePackages.npm
    
    # Python for backend
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Development tools
    git
    curl
    wget
    
    # Optional: VS Code extensions support
    # vscode-with-extensions
    
    # Optional: Docker for containerization
    docker
    docker-compose
  ];
  
  shellHook = ''
    echo "🚀 AI Генератор Презентаций - Development Environment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📦 Available tools:"
    echo "  - Node.js:  $(node --version)"
    echo "  - npm:      $(npm --version)"
    echo "  - Python:   $(python --version)"
    echo "  - pip:      $(pip --version)"
    echo ""
    echo "🎯 Quick start commands:"
    echo "  Frontend:   npm install && npm run dev"
    echo "  Backend:    python -m venv venv && source venv/bin/activate"
    echo ""
    echo "📚 Documentation:"
    echo "  - START_HERE.md          - Quick start guide"
    echo "  - ИНСТРУКЦИЯ.md          - Russian instructions"
    echo "  - README.md              - Full documentation"
    echo "  - DEMO_SCRIPT.md         - Hackathon demo script"
    echo ""
    echo "🎨 Rostelecom colors:"
    echo "  - Blue:    #0019B5  🔵"
    echo "  - Orange:  #FF4F12  🟠"
    echo "  - Purple:  #7700C7  🟣"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✨ Ready to build amazing presentations with AI!"
    echo ""
    
    # Set up Python virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
      echo "📦 Creating Python virtual environment..."
      python -m venv venv
      echo "✅ Virtual environment created!"
      echo "   Activate it with: source venv/bin/activate"
      echo ""
    fi
    
    # Install frontend dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
      echo "📦 Installing frontend dependencies..."
      npm install
      echo "✅ Frontend dependencies installed!"
      echo ""
    fi
    
    # Set environment variables
    export PROJECT_ROOT=$(pwd)
    export FRONTEND_PORT=5173
    export BACKEND_PORT=8000
    
    # Aliases for convenience
    alias frontend="npm run dev"
    alias backend="cd backend && python main.py"
    alias build="npm run build"
    alias serve="npm run preview"
    
    echo "💡 Useful aliases available:"
    echo "  - frontend    - Start frontend dev server"
    echo "  - backend     - Start backend server"
    echo "  - build       - Build for production"
    echo "  - serve       - Serve production build"
    echo ""
  '';
  
  # Python environment
  PYTHON_ENV = "development";
  
  # Environment variables for development
  NIX_SHELL_NAME = "ai-presentation-generator";
}
