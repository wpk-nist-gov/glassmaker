../src/glassMaker.py << EOF
record example.cmd
help
help makeBead
makeBead Al 2 O 10
makeBead Ti 2 O 10
help setTarget
setTarget Al 0 8 12 1
setTarget Ti 1 3 6 1
help initInventory
initInventory
help suggestNext
suggestNext
help addInventory
addInventory 8 3
suggestNext
addInventory 8 5
suggestNext
addInventory 8 4
suggestNext
help writeJSON
writeJSON example
quit
EOF

