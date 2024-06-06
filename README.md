# git-svn-compare
Tools to verify migrations from Subversion to Git

git-svn-compare.py
For SVN repos migrated to Git using git-svn. Note SVN metadata *must* be preserved in the Git commits. If you strip the metadata as part of the migration process this tool will not work.

Given a Subversion dump file (created with 'svnadmin dump') and a local copy of a Git repo, git-svn-compare.py will verify that every SVN revision has at least one git commit.
