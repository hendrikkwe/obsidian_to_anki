# Obsidian to anki 

Document your notes in the form of: 

```
- <Question>
	- <Answer>
```

And then run *python obsidian_to_anki.py -i path/to/md* or *python obsidian_to_anki.py -o path/to/folder*. The images are copied to anki and you can import the csv file that is stored in *safe_at* as declared in paths_config.py.

**You need to specify media_folder_anki, media_folder_obsidian, safe_at and vault first!** 
