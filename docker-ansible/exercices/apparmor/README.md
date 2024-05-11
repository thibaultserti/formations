# AppArmor

## Créer un lien

```bash
ln -s $PWD/docker-container /etc/apparmor.d/my-app
```

## Reload apparmor
```bash
sudo apparmor_parser -r /etc/apparmor.d/my-app
```
