// 假设使用Unity引擎
var roleImage = Resources.Load("Character/RoleImage.png") as Texture2D;
var roleSprite = Sprite.Create(roleImage, new Rect(0, 0, roleImage.width, roleImage.height), new Vector3(0.5f, 0.5f, 0f), 100f);
roleSprite.name = "RoleSprite";
transform.Find("Character").AddChild(roleSprite);