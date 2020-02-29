import cppyy

cppyy.cppdef("""
void look2(std::string myString) {
  if (const auto it = myString.find("World"); it != std::string::npos)
      std::cerr << it << " World\\n";
  else
      std::cerr << it << " not found!!\\n";
}
""")

from cppyy.gbl import look2

look2("Goodbye World")

