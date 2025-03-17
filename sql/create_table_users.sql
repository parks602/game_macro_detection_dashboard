CREATE TABLE [dbo].[users](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[username] [nvarchar](50) NOT NULL,
	[password_hash] [nvarchar](255) NOT NULL,
	[last_password_change] [datetime] NOT NULL,
	[role] [nvarchar](20) NULL,
	[created_at] [datetime] NULL,
	[email] [varchar](255) NULL
)
GO

-- id: 고유 식별자
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Unique identifier', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'id';

-- username: 사용자 이름
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Username of the user', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'username';

-- password_hash: 암호화된 비밀번호
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Encrypted password hash', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'password_hash';

-- last_password_change: 마지막 비밀번호 변경 날짜
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Last password change date', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'last_password_change';

-- role: 사용자 역할
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'User role (e.g., admin, user)', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'role';

-- created_at: 계정 생성 날짜
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Account creation timestamp', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'created_at';

-- email: 사용자 이메일
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'User email address', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'users', 
  @level2type=N'COLUMN', 
  @level2name=N'email';
