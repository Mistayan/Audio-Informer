# Audio-Informer

Logiciel en cours de développement.
Permet de scanner un fichier mp3, mp4, ogg, flac(, ...) pour chercher des tags supplémentaires sur le web.
Ou tous les fichiers dans un dossier donné

## Pré-requis
    - ffmpeg & ffprobe near main 

## Comment utiliser :
    main.py [fichier_audio |& dossier_de_fichiers_audio]

Le logiciel enregistre ses découvertes dans ./Results


### Tâches effectuées :

- [x] charger en mémoire les chemins des fichiers

- [x] multiprocessing de tâches (1 process par média, pour accélérer les recherches)
    - [x] Ouvrir un fichier Audio via son path, et lire ses tags (si disponibles)
    - [x] multithreading du process, pour les différentes recherches (plus shazam, qui est très gourmand)
    - [x] shazam du fichier pour trouver des infos supplémentaires (lyrics, writers, ...)
      - [x] récupérer la jaquette de l'album
    - [ ] En cours musicbrainz : récolte de tags de genres supplémentaires pour l'organisation des librairies
    - [x] sauvegarder les résultats dans ./Results
  
- [ ] Trier et comparer les résultats des recherches
    - [ ] calculer la probabilité que les données soient liées au fichier demandé
    - [ ] demander l'accord à l'utilisateur si le taux de compatibilité n'est pas > 95 %
    - [X] Enregistrer les tags demandés dans le fichier audio.