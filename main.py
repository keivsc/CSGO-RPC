from utils.main import main
import traceback
import pystray._win32

try:
    main()
except:
    traceback.print_exc()
    input()