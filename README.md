
##Synopsis

TagFS is a semantic system which is used to improve the user experience by adding tags to the files. These tags have relationship and can represented via our graph based model.

Please refer to our github repository for latest changes: <a>https://github.com/rahulpshah/tagfs</a>

##Code Example

Mount the directory on mountpoint

<code>tagfs ~/path/to/mount-dir ~/path/to/mountpoint</code>

Tag a file

<code>tag add filename tagname</code>

Add a relationship between tags

<code>tagrel add tag1 tag2</code> 

Retrieve files tagged as tag1

<code>getfiles tag1</code>


##Installation

In order to install the packages, please install the repository and run the setup.sh file from the project folder.

<code>sh setup.sh</code>

##Important Files

**database.py**        - used to create the database object and shoot the initial queries<br>
**graph.py**           - used to create the actual graphical representation of the tag-to-tag relationship<br>
**fuse-start.py** 	   - script that has all the user's level implementation of fuse<br>
**pythonInterface.py** - driver program to invoke fuse<br>

##Dependencies

<ol>
	<li>hachoir-metadata</li>
	<li>hachoir-core</li>
	<li>hachoir-parser</li>
	<li>pyechant</li>
	<li>docx2txt</li>
	<li>nltk</li>
</ol>

##Contributors
Gaurav Aradhye (garadhy@ncsu.edu)<br>
Rahul Shah (rshah5@ncsu.edu)<br>
Aniket Patel (apatel10@ncsu.edu)
